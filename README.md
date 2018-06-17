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

$ python manage.py makemigrations activitypub
$ python manage.py migrate
$ python manage.py collectstatic
$ python manage.py createsuperuser

```

nginxでHTTPS化して公開する準備。

```conf
server {
  listen 80;
  listen [::]:80;
  server_name example.com;
  return 301 https://$host$request_uri;
}

server {
  listen 443;
  server_name example.com;

  ssl_protocols TLSv1.2;
  ssl_ciphers HIGH:!MEDIUM:!LOW:!aNULL:!NULL:!SHA;
  ssl_prefer_server_ciphers on;
  ssl_session_cache shared:SSL:10m;

  ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/uwsgi.sock;
    }

    # メディアファイルの公開用
    location /static/ {
        alias /path/to/simple_ap/static/;
    }
    location /media/ {
        alias /path/to/simple_ap/media/;
    }}
```

djangoを立ち上げてWebサーバを公開

```
$ uwsgi --ini django.ini
```

https://~/admin から Account の情報を登録

現在のRSS情報の取得

```
$ python manage.py rss
```

cronでRSSの更新を確認

```
* * * * * /path/to/simple_ap/env/bin/python /path/to/simple_ap/rss_importer.py
```

flaskを立ち上げてAPIサーバを公開

```
$ uwsgi --ini flask.ini
```
