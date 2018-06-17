import requests
import json
from urllib.parse import urlparse
from httpsig import HeaderSigner
from datetime import datetime

def sign_headers(account, method, path):
    sign = HeaderSigner(account.ap_id(), account.private_key, algorithm='rsa-sha256', headers=['(request-target)', 'date']).sign({'Date': datetime.now().isoformat()}, method=method, path=path)
    auth = sign.pop('authorization')
    sign['Signature'] = auth[len('Signature '):] if auth.startswith('Signature ') else ''
    return sign

def post_accept(account, target, activity):
    to = target.inbox
    jsn = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'type': 'Accept',
        'actor': account.ap_id(),
        'object': activity,
    }
    headers = sign_headers(account, 'POST', urlparse(to).path)
    response = requests.post(to, json=jsn, headers=headers)
    if response.status_code >= 400 and response.status_code < 600:
        raise Exception('accept post error')
