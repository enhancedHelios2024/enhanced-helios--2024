
from django.dispatch import Signal
from .utils import classify_face
from helios_auth.security import get_user

# Define your function
def post_view_function(sender, request, response, **kwargs):
    user = get_user(request)
    classify_face(user, request, response)  
    pass

# Define your custom signal
post_request_signal = Signal()
