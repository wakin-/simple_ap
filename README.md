# simple_ap

## 要件
- python3
- virtualenv

## 使い方

```
$ git clone git@github.com:wakin-/simple_ap.git
$ cd simple_ap

$ pip install virtualenv
$ virtualenv env -p python3
$ source env/bin/activate

$ pip install -r requirements.txt

$ python manage.py makemigrations
$ python manage.py migration
$ python manage.py collectstatic

```
