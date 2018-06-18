#!/bin/sh

virtualenv env -p python3
source env/bin/activate

pip install -r requirements.txt
python manage.py makemigrations activitypub
python manage.py migrate
python manage.py loaddata fixture/setup.json
