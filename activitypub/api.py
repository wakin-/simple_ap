from flask import Flask, Response, request
from django.apps import apps
from django.conf import settings
apps.populate(settings.INSTALLED_APPS)
from .models import Account, Follower, Note
from .follow import follow, unfollow
import json
from .apps import app
from .lib import post_accept

@app.route('/<name>')
def account(name):
    account = Account.objects.filter(name=name).first()
    return Response(json.dumps(account.to_dict()), headers={'Content-Type': 'application/activity+json'}) if account else Response(status=404)

@app.route('/<name>/pubkey')
def pubkey(name):
    account = Account.objects.filter(name=name).first()
    return Response(json.dumps(account.key_to_dict()), headers={'Content-Type': 'application/activity+json'}) if account else Response(status=404)

@app.route('/<name>/<note_id>/')
def note(name, note_id):
    account = Account.objects.filter(name=name).first()
    note = Note.objects.filter(id=int(note_id), account=account).first()
    return Response(json.dumps(note.to_dict()), headers={'Content-Type': 'application/activity+json'}) if note else Response(status=404)

@app.route('/<name>/inbox', methods=['POST'])
def inbox(name):
    print(request.headers)
    if request.headers['Content-Type'] != 'application/activity+json' or 'type' not in request.json:
        return Response(status=400)

    account = Account.objects.filter(name=name).first()
    jsn = request.json
    if not account or type(jsn)!=dict or 'type' not in jsn:
        return Response(status=400)
    elif jsn['type'] == 'Follow' and 'actor' in jsn:
        try:
            follower = follow(account, jsn['actor'])
            post_accept(account, follower, jsn)
        except:
            return Response(status=500)
        return Response(status=200)
    elif jsn['type'] == 'Undo':
        obj = jsn['object']
        if type(obj)!=dict or 'type' not in obj:
            return Response(status=400)
        elif obj['type'] == 'Follow' and 'actor' in obj:
            try:
                unfollower = unfollow(account, obj['actor'])
                post_accept(account, unfollower, jsn)
            except:
                return Response(status=500)
            return Response(status=200)

    return Response(status=501)

@app.route('/<name>/outbox')
def outbox(name):
    return Response(status=501)
