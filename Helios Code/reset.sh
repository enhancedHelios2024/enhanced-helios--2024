#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.
dropdb helios2
createdb helios2
#python manage.py makemigrations
python3 manage.py makemigrations
#python manage.py migrate
python3 manage.py migrate
echo "from helios_auth.models import User; User.objects.create(user_type='google',user_id='ben@adida.net', info={'name':'Ben Adida'})" | python3 manage.py shell