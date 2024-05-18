# import os
# import sys






# print(sys.path)

# import os
# import django
# import sys
# import helios
# Set the DJANGO_SETTINGS_MODULE environment variable.
# os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# print(sys.path)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
# print(helios.__file__)
# Initialize Django.
# django.setup()

#IMPORTANT WHEN YOU GET HELIOS NOT FOUND: export PYTHONPATH=""


import os
import sys
# from django.core.management import setup
import django

# Set the environment variable to your Django project's settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# Call setup to initialize Django
django.setup()

# Now you can import your Django models
from helios.models import Voter
print(Voter.objects.all())

# Your code here
