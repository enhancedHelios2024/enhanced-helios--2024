from django.core.management import call_command

call_command('collectstatic', interactive=False)
