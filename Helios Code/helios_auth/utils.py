"""
Some basic utils 
(previously were in helios module, but making things less interdependent

2010-08-17
"""
import hashlib
import json
import face_recognition as fr
import numpy as np
from PIL import Image, ImageDraw
import base64
import random
from io import BytesIO
from django.dispatch import Signal
from django.core.files.base import ContentFile
from django.contrib.auth import get_user
import face_recognition
import base64
import numpy as np
import cv2
import io
import face_recognition
import base64
import numpy as np
import cv2
import os
import json
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
import psycopg2

def compare_faces(base64_str1, base64_str2):
  try:
      # Decode Base64 strings into image data
      img_data1 = base64.b64decode(base64_str1)
      img_data2 = base64.b64decode(base64_str2)

      # Convert image data into numpy arrays
      nparr1 = np.frombuffer(img_data1, np.uint8)
      nparr2 = np.frombuffer(img_data2, np.uint8)

      # Decode numpy arrays into RGB images
      img1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
      img2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)

      # Detect face locations in the images
      face_locations1 = face_recognition.face_locations(img1)
      face_locations2 = face_recognition.face_locations(img2)

      # Check if exactly one face is detected in each image
      if len(face_locations1) == 1 and len(face_locations2) == 1:
          # Encode face encodings for comparison
          face_encodings1 = face_recognition.face_encodings(img1, face_locations1)[0]
          face_encodings2 = face_recognition.face_encodings(img2, face_locations2)[0]

          # Compare the face encodings
          face_distance = face_recognition.face_distance([face_encodings1], face_encodings2)[0]

          # Return the face distance (0 for identical faces, higher values for more dissimilar faces)
          return face_distance

      else:
          print("Error: Could not detect exactly one face in each image.")

  except Exception as e:
      print("Error occurred during face comparison:", e)
      return None
# post_classify_face_signal = Signal()


def decode_base64_image(image_string):
    """Decode a base64 image string into a PIL Image object."""
    image_bytes = base64.b64decode(image_string)
    image = Image.open(BytesIO(image_bytes))
    width, height = image.size
    return image, width, height

def encode_image_to_base64(image):
    """Encode a PIL Image object to a base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def generate_visual_cryptography_shares(original_image):
    """Generate two shares of a visual cryptography scheme."""
    width, height = original_image.size

    r_list = []
    r_random_list = []
    g_list = []
    g_random_list = []
    b_list = []
    b_random_list = []

    for y in range(height):
        for x in range(width):
            pixel = original_image.getpixel((x, y))
            r,g,b = pixel
            r_random_val = random.randint(1, 1000)
            r_random_list.append(r_random_val)
            g_random_val = random.randint(1, 1000)
            g_random_list.append(g_random_val)
            b_random_val = random.randint(1, 1000)
            b_random_list.append(b_random_val)
            r_list.append(r * r_random_val)
            g_list.append(g * g_random_val)
            b_list.append(b * b_random_val)

    random_val = random.randint(1 , 3)
    if random_val == 1:
        server_list = r_list
        # server_list.append("r")
        client_list1 = g_list
        client_list1.append("g")
        client_list2 = b_list
        client_list2.append("b")
    elif random_val == 2:
        server_list = g_list
        # server_list.append("g")
        client_list1 = r_list 
        client_list1.append("r")  
        client_list2 = b_list
        client_list2.append("b")
    else:
        server_list = b_list
        # server_list.append("b")
        client_list1 = r_list
        client_list1.append("r")
        client_list2 = g_list
        client_list2.append("g")

    return server_list, client_list1, client_list2, r_random_list, g_random_list, b_random_list


def combine_shares_to_recreate_image(s_list, c1_list, c2_list, width, height, r_random_list, g_random_list, b_random_list):
    """Combine two shares to recreate the original image."""
    # width, height = share1.size
    length = len(s_list) 
    last_c1 = c1_list[len(c1_list) - 1]
    last_c2 = c2_list[len(c2_list) - 1]
    # c1_list.pop()
    # c2_list.pop()
    # print("size of c1 list")
    # print(str(len(c1_list)))
    # combined_tuple = ()
    combined_tuple = ()
    combined_tuples = []

    for i in range(height):
        row_tuples = []
        for j in range(width):
            index = i * width + j
            if last_c1 == "r" and last_c2 == "g":
                combined_tuple = (int(c1_list[index]/r_random_list[index]), int(c2_list[index]/g_random_list[index]), int(s_list[index]/b_random_list[index]))
            elif last_c1 == "r" and last_c2 == "b":
                combined_tuple = (int(c1_list[index]/r_random_list[index]), int(s_list[index]/g_random_list[index]), int(c2_list[index]/b_random_list[index]))
            elif last_c1 == "g" and last_c2 == "b":
                combined_tuple = (int(s_list[index]/r_random_list[index]), int(c1_list[index]/g_random_list[index]), int(c2_list[index]/b_random_list[index]))
            else:
                combined_tuple = (0, 0, 0)  # Default tuple if conditions not met
            row_tuples.append(combined_tuple)
        combined_tuples.append(row_tuples)


    image = Image.new("RGB", (width, height))
    # print(combined_tuples)

    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), combined_tuples[y][x])

    # image.show("Reconstructed Image")  
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    base64_image = base64.b64encode(image_bytes.getvalue()).decode()

    return base64_image


## JSON
def to_json(d):
    return json.dumps(d, sort_keys=True)


def from_json(value):
    if value == "" or value is None:
        return None

    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception as e:
            # import ast
            # try:
            #     parsed_value = ast.literal_eval(parsed_value)
            # except Exception as e1:
            raise Exception("value is not JSON parseable, that's bad news") from e

    return value


def JSONFiletoDict(filename):
    with open(filename, 'r') as f:
        content = f.read()
    return from_json(content)




def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_encoded_faces():
    from profiles.models import Profile
    """
    This function loads all user 
    profile images and encodes their faces
    """
    # Retrieve all user profiles from the database

    qs = Profile.objects.all()

    # Create a dictionary to hold the encoded face for each user
    encoded = {}

    for p in qs:
        # Initialize the encoding variable with None
        encoding = None

        # Load the user's profile image
        face = fr.load_image_file(p.photo.path)

        # Encode the face (if detected)
        face_encodings = fr.face_encodings(face)
        if len(face_encodings) > 0:
            encoding = face_encodings[0]
        else:
            print("No face found in the image")

        # Add the user's encoded face to the dictionary if encoding is not None
        if encoding is not None:
            encoded[p.user.user_id] = encoding

    # Return the dictionary of encoded faces
    return encoded


def classify_face(user, request, response, **kwargs):
    

    if user.has_face_image():
        # print("USER HAS FACE IMAGE NO NEED TO SAVE ANYTHING")
        response_data = response.content.decode('utf-8')  
        response_dict = json.loads(response_data)
        response_value = response_dict.get('response', None)
        img = response_value

        # print("USER HAS FACE IMAGE NO NEED TO SAVE ANYTHING")
    else:
        # img = response
        # print("RESPONSE FROM FACIAL RECOGNITION")
        # print(response)
        img = response
        face_image, width, height = decode_base64_image(img)
        server, c1, c2, r_random, g_random, b_random = generate_visual_cryptography_shares(face_image)

        # Construct the desktop path
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        if c1[len(c1) - 1] == "r" and c2[len(c2) - 1] == "g":
            r1_string = ' '.join(map(str, b_random))
            random_1 = json.dumps(r_random)
            user.random_1 = random_1
            user.save()
            random_2 = json.dumps(g_random)
            user.random_2 = random_2
            user.save()   
        elif c1[len(c1) - 1] == "r" and c2[len(c2) - 1] == "b":
            r1_string = ' '.join(map(str, g_random))
            random_1 = json.dumps(r_random)
            user.random_1 = random_1
            user.save()
            random_2 = json.dumps(b_random)
            user.random_2 = random_2
            user.save()
        elif c1[len(c1) - 1] == "g" and c2[len(c2) - 1] == "b":
            r1_string = ' '.join(map(str, r_random))
            random_1 = json.dumps(g_random)
            user.random_1 = random_1
            user.save()
            random_2 = json.dumps(b_random)
            user.random_2 = random_2
            user.save()
        

        # file_path_3 = os.path.join(desktop_path, 'r3.txt')
        # with open(file_path_3, 'w') as file:
        #     file.write(r1_string)

        # Save server_user_face_share
        server_share_json = json.dumps(server)
        user.server_user_face_share = server_share_json
        user.save()
        c1_string = ' '.join(map(str, c1))
        c2_string = ' '.join(map(str, c2))

        profile = user.profile
        # print("USER EMAIL")
        # print(str(profile))
        hashed_string = hashlib.sha256(str(profile).encode()).hexdigest()
        # print("HASHED STRING")
        # print(hashed_string)
        connection = psycopg2.connect(
            host="localhost",  # Connect to localhost since you're forwarding the service locally
            port="5433",       # Use the local port that you forwarded to (5433)
            database="postgresdb",
            user="postgresadmin",
            password="admin123"
        )
        cursor = connection.cursor()
        cursor.execute("INSERT INTO user_face_shares (email_hash, file1, file2, file3) VALUES (%s, %s, %s, %s)",
                   (hashed_string,c1_string, c2_string, r1_string))
        connection.commit()
        cursor.close()
        connection.close()

        # messages.success(request, 'Shares have been saved on the two different servers.')
        # i want to add a message to check in the unit test
        # show me how 


        # print("SAVING USER FACE IMAGE ON CLIENT DEVICE AND IN SERVER")

        return redirect('/')

def compare_faces(base64_str1, base64_str2):
    try:
        # Decode Base64 strings into image data
        img_data1 = base64.b64decode(base64_str1)
        img_data2 = base64.b64decode(base64_str2)

        # Convert image data into numpy arrays
        nparr1 = np.frombuffer(img_data1, np.uint8)
        nparr2 = np.frombuffer(img_data2, np.uint8)

        # Decode numpy arrays into RGB images
        img1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
        img2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)

        # Detect face locations in the images
        face_locations1 = face_recognition.face_locations(img1)
        face_locations2 = face_recognition.face_locations(img2)

        # Check if exactly one face is detected in each image
        if len(face_locations1) == 1 and len(face_locations2) == 1:
            # Encode face encodings for comparison
            face_encodings1 = face_recognition.face_encodings(img1, face_locations1)[0]
            face_encodings2 = face_recognition.face_encodings(img2, face_locations2)[0]

            # Compare the face encodings
            face_distance = face_recognition.face_distance([face_encodings1], face_encodings2)[0]

            # Return the face distance (0 for identical faces, higher values for more dissimilar faces)
            return face_distance

        else:
            print("Error: Could not detect exactly one face in each image.")

    except Exception as e:
        print("Error occurred during face comparison:", e)
        return None