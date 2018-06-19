#!/bin/sh

sudo apt install -y python3 python3-dev virtualenv supervisor

virtualenv env -p python3

env/bin/pip install -r requirements.txt
env/bin/python manage.py makemigrations activitypub
env/bin/python manage.py migrate
env/bin/python manage.py loaddata fixture/setup.json

cp simple_ap.conf.example simple_ap.conf
echo directory=$PWD >> simple_ap.conf
echo command=$PWD/env/bin/uwsgi --ini flask.ini >> simple_ap.conf
echo user=$USER >> simple_ap.conf
sudo mv simple_ap.conf /etc/supervisor/conf.d/
sudo supervisorctl reload
