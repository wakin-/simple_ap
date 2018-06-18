# simple_ap

RSSフィードを定期チェックして更新情報をActivityPubでフォロワーに配信するAPIサーバです。APIサーバはflaskを使い、DB周りはdjangoを使ってます。Mastodonとの連携を想定しています。

## 要件
- Ubuntu
- nginx等Webサーバ
- SSL/TLS証明書

## 使い方

```
$ git clone git@github.com:wakin-/simple_ap.git
$ cd simple_ap
$ vi fixture/setup.json
```

初期データの準備。

```json:fixture/setup.json
[
  {
    "model": "activitypub.account",
    "pk": 1,
    "fields": {
      "name": "<アカウントID 半角英数-_>",
      "display_name": "<表示名>",
      "feed_url": "<RSSフィードのURL>",
      "icon": "<アイコンのパス>"
    }
  }
]
```

セットアップスクリプトの実行。

```
$ chmod +x setup.sh
$ ./setup.sh
```

nginxでHTTPS化して公開する例。

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
    location /media/ {
        alias /path/to/simple_ap/media/;
    }
}
```

現在のRSS情報を取得。

```
$ python manage.py rss
```

cronで定期的にRSSの更新を確認。新着があればPOST。

```
* * * * * /path/to/simple_ap/env/bin/python /path/to/simple_ap/rss_importer.py
```

外部インスタンスの検索エリアから https://~/<name> でアカウントを検索し、リモートフォロー。
