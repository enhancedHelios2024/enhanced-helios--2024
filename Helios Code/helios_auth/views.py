"""
Views for authentication

Ben Adida
2009-07-05
"""

# import utils
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import hashlib
import psycopg2
import json
from urllib.parse import urlencode
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import settings
from helios_auth import DEFAULT_AUTH_SYSTEM, ENABLED_AUTH_SYSTEMS
from helios_auth.security import get_user
from helios_auth.url_names import AUTH_INDEX, AUTH_START, AUTH_AFTER, AUTH_WHY, AUTH_AFTER_INTERVENTION
from .auth_systems import AUTH_SYSTEMS, password
from .models import User
from .security import FIELDS_TO_SAVE
from .view_utils import render_template, render_template_raw
from .utils import is_ajax, classify_face, combine_shares_to_recreate_image, compare_faces
import base64
from logs.models import Log
from django.core.files.base import ContentFile
from helios_auth.models import User
from profiles.models import Profile
from django.contrib.auth import logout, login
from django.shortcuts import render
from .signals import post_request_signal
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
import ast
import numpy as np
import cv2
from django.contrib import messages
from django.utils import timezone 
from datetime import datetime


def index(request):
    """
    the page from which one chooses how to log in.
    """
    return_url = request.GET.get('return_url')
    # print("RETURN URL FROM INDEX VIEW")
    # print(return_url)
    request.session['auth_return_url'] = return_url
    # print("INDEX VIEW")
    # print(request.session.get('authentication_step', 0))
    user = get_user(request)

    # single auth system?
    if len(ENABLED_AUTH_SYSTEMS) == 1 and not user:
        return HttpResponseRedirect(reverse(AUTH_START, args=[ENABLED_AUTH_SYSTEMS[0]]) + '?return_url=' + request.GET.get('return_url', ''))

    # if DEFAULT_AUTH_SYSTEM and not user:
    #  return HttpResponseRedirect(reverse(start, args=[DEFAULT_AUTH_SYSTEM])+ '?return_url=' + request.GET.get('return_url', ''))

    default_auth_system_obj = None
    if DEFAULT_AUTH_SYSTEM:
        default_auth_system_obj = AUTH_SYSTEMS[DEFAULT_AUTH_SYSTEM]

    # form = password.LoginForm()

    return render_template(request, 'index', {'return_url': request.GET.get('return_url', '/'),
                                              'enabled_auth_systems': ENABLED_AUTH_SYSTEMS,
                                              'default_auth_system': DEFAULT_AUTH_SYSTEM,
                                              'default_auth_system_obj': default_auth_system_obj,
                                              'authentication_step': request.session.get('authentication_step', 0)})


def login_box_raw(request, return_url='/', auth_systems=None):
    """
    a chunk of HTML that shows the various login options
    """
    default_auth_system_obj = None
    if DEFAULT_AUTH_SYSTEM:
        default_auth_system_obj = AUTH_SYSTEMS[DEFAULT_AUTH_SYSTEM]

    # make sure that auth_systems includes only available and enabled auth systems
    if auth_systems is not None:
        enabled_auth_systems = set(auth_systems).intersection(
            set(ENABLED_AUTH_SYSTEMS)).intersection(set(AUTH_SYSTEMS.keys()))
    else:
        enabled_auth_systems = set(ENABLED_AUTH_SYSTEMS).intersection(
            set(AUTH_SYSTEMS.keys()))

    form = password.LoginForm()

    return render_template_raw(request, 'login_box', {
        'enabled_auth_systems': enabled_auth_systems, 'return_url': return_url,
        'default_auth_system': DEFAULT_AUTH_SYSTEM, 'default_auth_system_obj': default_auth_system_obj,
        'form': form})


def do_local_logout(request):
    """
    if there is a logged-in user, it is saved in the new session's "user_for_remote_logout"
    variable.
    """

    user = None

    if 'user' in request.session:
        user = request.session['user']

    # 2010-08-14 be much more aggressive here
    # we save a few fields across session renewals,
    # but we definitely kill the session and renew
    # the cookie
    field_names_to_save = request.session.get(FIELDS_TO_SAVE, [])

    # let's clean up the self-referential issue:
    field_names_to_save = set(field_names_to_save)
    field_names_to_save = field_names_to_save - {FIELDS_TO_SAVE}
    field_names_to_save = list(field_names_to_save)

    fields_to_save = dict([(name, request.session.get(name, None))
                          for name in field_names_to_save])

    # let's not forget to save the list of fields to save
    fields_to_save[FIELDS_TO_SAVE] = field_names_to_save

    request.session.flush()

    for name in field_names_to_save:
        request.session[name] = fields_to_save[name]

    # copy the list of fields to save
    request.session[FIELDS_TO_SAVE] = fields_to_save[FIELDS_TO_SAVE]

    request.session['user_for_remote_logout'] = user


def do_remote_logout(request, user, return_url="/"):
    # FIXME: do something with return_url
    auth_system = AUTH_SYSTEMS[user['type']]

    # does the auth system have a special logout procedure?
    user_for_remote_logout = request.session.get(
        'user_for_remote_logout', None)
    del request.session['user_for_remote_logout']
    if hasattr(auth_system, 'do_logout'):
        response = auth_system.do_logout(user_for_remote_logout)
        return response


def do_complete_logout(request, return_url="/"):
    do_local_logout(request)
    user_for_remote_logout = request.session.get(
        'user_for_remote_logout', None)
    if user_for_remote_logout:
        response = do_remote_logout(
            request, user_for_remote_logout, return_url)
        return response
    return None


def logout(request):
    """
    logout
    """

    return_url = request.GET.get('return_url', "/")
    request.session['authentication_step'] = 0
    response = do_complete_logout(request, return_url)
    if response:
        return response

    return HttpResponseRedirect(return_url)


def _do_auth(request):
    # the session has the system name
    system_name = request.session['auth_system_name']

    # get the system
    system = AUTH_SYSTEMS[system_name]

    # where to send the user to?
    redirect_url = settings.SECURE_URL_HOST + reverse(AUTH_AFTER)
    auth_url = system.get_auth_url(request, redirect_url=redirect_url)

    if auth_url:
        return HttpResponseRedirect(auth_url)
    else:
        return HttpResponse("an error occurred trying to contact " + system_name + ", try again later")


def start(request, system_name):
    if not (system_name in ENABLED_AUTH_SYSTEMS):
        return HttpResponseRedirect(reverse(AUTH_INDEX))

    # why is this here? Let's try without it
    # request.session.save()

    # store in the session the name of the system used for auth
    request.session['auth_system_name'] = system_name

    # where to return to when done
    #

    # if request.session['auth_return_url'] == '/':

    #   request.session['auth_return_url'] = request.GET['return_url']
    # else:
    #   request.session['auth_return_url'] = '/'

    request.session['auth_return_url'] = request.GET.get('return_url', '/')

    return _do_auth(request)


def perms_why(request):
    if request.method == "GET":
        return render_template(request, "perms_why")

    return _do_auth(request)


def after(request):
    # which auth system were we using?
    if 'auth_system_name' not in request.session:
        do_local_logout(request)
        return HttpResponseRedirect("/")

    system = AUTH_SYSTEMS[request.session['auth_system_name']]

    # get the user info
    user = system.get_user_info_after_auth(request)

    if user:
        # get the user and store any new data about him
        user_obj = User.update_or_create(
            user['type'], user['user_id'], user['name'], user['info'], user['token'])

        request.session['user'] = user
    else:
        return HttpResponseRedirect("%s?%s" % (reverse(AUTH_WHY), urlencode({'system_name': request.session['auth_system_name']})))

    # does the auth system want to present an additional view?
    # this is, for example, to prompt the user to follow @heliosvoting
    # so they can hear about election results
    if hasattr(system, 'user_needs_intervention'):
        intervention_response = system.user_needs_intervention(
            user['user_id'], user['info'], user['token'])
        if intervention_response:
            return intervention_response

    # go to the after intervention page. This is for modularity
    return HttpResponseRedirect(reverse(AUTH_AFTER_INTERVENTION))


def after_intervention(request):
    return_url = "facial_recognition"
    # success = find_user_view(request)
    # if success:
    #   return HttpResponseRedirect(settings.URL_HOST + 'main')

    # if 'auth_return_url' in request.session:
    #   return_url = request.session['auth_return_url']
    #   del request.session['auth_return_url']

    # return HttpResponseRedirect(settings.URL_HOST + return_url)
    return HttpResponseRedirect(return_url)


# DONT KNOW YET
def login_view(request):
    # request.session['authentication_step'] = 1
    return render_template(request, 'login', {})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home_view(request):
    return render_template(request, 'main.html', {})


def find_user_view(request):
    # attempt_counter = request.session.get('attempt_counter', 0)

    # if attempt_counter >= 3:
    #   request.session.flush()
    #   return JsonResponse({'success': False, 'message': 'Maximum attempts reached. Session ended.'})
    # if is_ajax(request):
    photo = request.POST.get('images')

    #   data = json.loads(request.body.decode('utf-8'))
    #   photo = data.get('photo')

    #   _, str_img = photo.split(';base64')
    #   decoded_file = base64.b64decode(str_img)
    #   x = Log()
    #   x.photo = ContentFile(decoded_file, 'upload.png')
    #   x.save()
    #   res = classify_face(x.photo.path)
    #   user_exists = User.objects.filter(user_id=res).exists()
    #   if user_exists:
    #     user = User.objects.get(user_id=res)
    #     profile = Profile.objects.get(user=user)
    #     x.profile = profile
    #     x.save()
    #     login(request,user)
    #     print("SUCCESS")
    #     print("USER IS " + str(user))
    #     print("SUCCESS")
    #     request.session['attempt_counter'] = 0
    #     return JsonResponse({'success': True, 'redirect_url': reverse('auth@after')})
    #   else:
    #       request.session['attempt_counter'] = attempt_counter + 1
    #       print("FAILURE")
    #       print("FAILURE")

    #       return JsonResponse({'success': False, 'message': 'Invalid user. Attempts remaining: {}'.format(3 - attempt_counter), 'redirect_url': reverse('facial_recognition')})
    # return HttpResponseRedirect(settings.URL_HOST + 'facial_recognition')


def facial_recognition(request):
    # print("FACIAL RECOGNITION VIEW")
    user = get_user(request)
    user_data = {
        'name': user.name,
        'server_user_face_share': user.server_user_face_share,
        'profile': str(user.profile),
    }
    user_json = json.dumps(user_data, cls=DjangoJSONEncoder)
    return render(request, 'facial_recognition.html', {'user_json': user_json, 'MASTER_HELIOS': settings.MASTER_HELIOS, 'SITE_TITLE': settings.SITE_TITLE})



def recombine_shares(request):
    # print("RECOMBINE SHARES VIEW")
    # request.session['authentication_step'] = 2
    # print(request.user.is_authenticated)
    if request.method == 'POST':
        data = json.loads(request.body)
        c1_array = data.get('file1Array', [])
        c2_array = data.get('file2Array', [])
        server_random_array = data.get('file3Array', [])
        base_64_str_2 = data.get('mainResponse', '')

        user = get_user(request)
        server_array = json.loads(user.server_user_face_share)
        c1_random_array = json.loads(user.random_1)
        c2_random_array = json.loads(user.random_2)

        if c1_array[len(c1_array) - 1] == "r" and c2_array[len(c2_array) - 1] == "g":
            base_64_str_1 = combine_shares_to_recreate_image(
                server_array, c1_array, c2_array, 1280, 720, c1_random_array, c2_random_array, server_random_array)
        elif c1_array[len(c1_array) - 1] == "r" and c2_array[len(c2_array) - 1] == "b":
            base_64_str_1 = combine_shares_to_recreate_image(
                server_array, c1_array, c2_array, 1280, 720, c1_random_array, server_random_array, c2_random_array)
        elif c1_array[len(c1_array) - 1] == "g" and c2_array[len(c2_array) - 1] == "b":
            base_64_str_1 = combine_shares_to_recreate_image(
                server_array, c1_array, c2_array, 1280, 720, server_random_array, c1_random_array, c2_random_array)

        similarity_index = compare_faces(base_64_str_1, base_64_str_2)
        # print("Last bits of base_64_str_1 " + base_64_str_1[-100:])
        # print("Last bits of base_64_str_2 " + base_64_str_2[-100:])
        # print("SECOND STRING LENGTH IS " + str(len(base_64_str_2)))
        # print("SIMILARITY INDEX IS " + str(similarity_index))

        # request.session['attempt_counter'] = 1

        attempt_counter = request.session.get('attempt_counter', 0)
        max_attempts = 3
        attempts_left = max_attempts - attempt_counter

        if 'attempt_timestamp' in request.session:
            cooldown_time = 3600 * 12 # CHANGE TO 12 HOURS
            max_attempt_time_str = request.session['attempt_timestamp']
            max_attempt_time = datetime.fromisoformat(max_attempt_time_str)
            elapsed_time = timezone.now() - max_attempt_time

            if elapsed_time.total_seconds() < cooldown_time:
              remaining_time_seconds = cooldown_time - elapsed_time.total_seconds()
              remaining_hours = int(remaining_time_seconds // 3600)
              remaining_minutes = int((remaining_time_seconds % 3600) // 60)
              remaining_seconds = int(remaining_time_seconds % 60)
                
              remaining_time_str = f'{remaining_hours} hours, {remaining_minutes} minutes, and {remaining_seconds} seconds'
                
              return JsonResponse({'message': f'Please wait {remaining_time_str} before attempting again.'})
        if similarity_index is not None and similarity_index <= 0.45:
            # request.user.is_authenticated = True
            if 'attempt_timestamp' in request.session:
                del request.session['attempt_timestamp']
            # print("SIMILARITY INDEX IS LESS THAN 0.5")
            request.session['authentication_step'] = 3
            # print(request.session['authentication_step'])
            # print(request.session['authentication_step'])
            # print(request.session['authentication_step'])
            # request.user.is_authenticated = True
            # print(request.session['authentication_step'])
            # request.user.is_authenticated = True
            redirect_url = reverse('auth@index')
            if 'auth_return_url' in request.session:
                if request.session['auth_return_url'] != '/' and request.session['auth_return_url'] != '':
                    redirect_url = request.session['auth_return_url']
                else:
                    redirect_url = reverse('auth@index')
            # print("REDIRECT URL IS " + redirect_url)
            return JsonResponse({'redirect_url': redirect_url, 'authentication_step': request.session['authentication_step'], 'message' : 'Authentication successful.'})
        elif similarity_index is not None and similarity_index > 0.45:
            # request.user.is_authenticated = False
            if attempts_left > 0:
                request.session['attempt_counter'] = attempt_counter + 1
                return JsonResponse({'message': f'Authentication unsuccessful. {attempts_left} attempts left.'})
            else:
                request.session.clear()
                redirect_url = '/'  # Adjust the URL name as needed
                request.session['attempt_timestamp'] = timezone.now().isoformat()
                return JsonResponse({'redirect_url': redirect_url, 'message': 'Maximum attempts reached. Session ended.'})
                # if 'attempt_counter' not in request.session:
                #     request.session['attempt_counter'] = 1
                # else:
                #     request.session['attempt_counter'] += 1

                # if request.session['attempt_counter'] > 3:
                #     request.session.flush()
                #     return redirect('home_logged_out_url')
                # else:
                #     return redirect('initial_auth_page_url') + '?alert=unsuccessful'
        else:
            return JsonResponse({'message': 'Authentication unsuccessful. The scan could not be read successfully. Please try again.'}, status=200)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


# s_list, c1_list, c2_list, width, height, r_random_list, g_random_list, b_random_list

def classify_face_view(request):
    # print("CLASSIFY FACE VIEW")
    # print("request method is " + request.method)
    if request.method == 'POST':
        try:
            # Assuming your data is a JSON object, you can adjust this based on your actual data format
            response_data = request.POST.get('response', '')
            # print("RESPONSE DATAAAAAAAAAAAAAAAA")
            # print(response_data)
            user = get_user(request)
            classify_face(user, request, response_data)

            # Perform face classification logic here
            # You may use a machine learning model or any other logic based on your requirements
            # print("RESPONSE DATA LENGTH ")
            # print("RESPONSE DATA LENGTH ")
            # print("RESPONSE DATA LENGTH ")
            # print(len(response_data))
            message1 = 'Registration susccessful. You can now log in.'
            redirect_url = '/'
            # message2 = 'Three files have been saved to your desktop. These files need to be saved in a secure location and kept with the same names. Please do not lose them. You will need them to log in again.'
            if 'auth_return_url' in request.session:
                if request.session['auth_return_url'] != '/' and request.session['auth_return_url'] != '':
                    redirect_url = request.session['auth_return_url']
                else:
                    logout(request)
                    redirect_url = '/'
            # print("REDIRECT URL IS " + redirect_url)
            return JsonResponse({'redirect_url': redirect_url, 'message1': message1})

        except Exception as e:
            # Handle exceptions if any
            return JsonResponse({'error': str(e)}, status=500)

    else:
        # Return an error response for non-POST requests
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_other_shares(request):
    # print("GET OTHER SHARES")
    # print("GET OTHER SHARES")

    user = request.GET
    user_email = list(user.keys())[0]
    # print("PROFILE IS " + str(user_email))
    hashed_profile_string = hashlib.sha256(
        str(user_email).encode()).hexdigest()

    # Establish connection to PostgreSQL database
    connection = psycopg2.connect(
        host="localhost",  # Connect to localhost since you're forwarding the service locally
        port="5433",       # Use the local port that you forwarded to (5433)
        database="postgresdb",
        user="postgresadmin",
        password="admin123"
    )

    # Create a cursor to perform database operations
    cursor = connection.cursor()

    # Query the database to fetch the corresponding record based on the hashed profile string
    cursor.execute(
        "SELECT file1, file2, file3 FROM user_face_shares WHERE email_hash = %s", (hashed_profile_string,))
    record = cursor.fetchone()  # Fetch the first matching record
    c1_string, c2_string, r1_string = record

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return JsonResponse({'c1': c1_string, 'c2': c2_string, 'r1': r1_string})
