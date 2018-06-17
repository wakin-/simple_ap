import json
from xml.dom.minidom import parseString
import re
from flask import Flask, jsonify, Response, request
from django.conf import settings
from activitypub.api import app
from activitypub.models import Account

@app.route('/.well-known/host-meta')
def webfinger_host_meta():
    xml_str = "<?xml version=\"1.0\"?>\
        <XRD xmlns=\"http://docs.oasis-open.org/ns/xri/xrd-1.0\">\
            <Link rel=\"lrdd\" type=\"application/xrd+xml\" template=\""+settings.SERVER_URL+"/.well-known/webfinger?resource={uri}\"/>\
        </XRD>"
    dom = parseString(xml_str)

    return Response(dom.toprettyxml(), headers={'Content-Type': 'application/xml'})

@app.route('/.well-known/webfinger')
def webfinger_resource():
    uri = request.args.get('resource')
    m = re.match('^acct:([a-zA-Z0-9_\-]+)@([a-zA-Z0-9_\-\.]+)', uri)
    subject, username, domain = m.group(0, 1, 2) if m else [None, None, None]
    account = Account.objects.filter(name=username).first()
    if domain != settings.DOMAIN or account is None:
        return Response(status=404)

    response = {
        'subject': subject,
        'links': [
            {
                'rel':  'self',
                'type': 'application/activity+json',
                'href': 'https://'+domain+'/'+username
            },
        ]
    }

    return jsonify(response)
