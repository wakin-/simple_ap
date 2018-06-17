import uuid
import os
import json
import magic
import requests
from urllib.parse import urlparse
from django.db import models
from django.conf import settings
from Crypto.PublicKey import RSA
from Crypto import Random
from .lib import sign_headers

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

class Account(BaseModel):
    name        = models.CharField(max_length=32, default='')
    feed_url    = models.CharField(max_length=255, default='')
    private_key = models.TextField(default='')
    public_key  = models.TextField(default='')

    def get_image_path(self, filename):
        prefix = 'images/'
        name = str(uuid.uuid4()).replace('-', '')
        extension = os.path.splitext(filename)[-1]
        return prefix + name + extension
    icon     = models.ImageField(upload_to=get_image_path)

    def __str__(self):
        return self.name

    def delete_file(path):
        if os.path.isfile(path):
            os.remove(path)
    def create_key_pair():
        rsa = RSA.generate(2048, Random.new().read)
        return [rsa.exportKey().decode('utf-8'), rsa.publickey().exportKey().decode('utf-8')]
    def save(self, *args, **kwargs):
        previous = Account.objects.filter(pk=self.pk).first()
        if previous and previous.icon != self.icon:
            Account.delete_file(settings.MEDIA_ROOT+'/'+previous.icon.name)
        else:
            self.private_key, self.public_key = Account.create_key_pair()
        super(Account, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        Account.delete_file(settings.MEDIA_ROOT+'/'+self.icon.name)
        super(Account, self).delete(*args, **kwargs)

    def ap_id(self):
        return settings.SERVER_URL+'/'+self.name

    def key_to_dict(self):
       return {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'type': 'Key',
            'id': self.ap_id()+'/pubkey',
            'owner': settings.SERVER_URL+'/'+self.name,
            'publicKeyPem': self.public_key
        } 

    def mimetype_from_path(self, path):
        return magic.Magic(mime=True).from_file(path)
    def to_dict(self):
        return {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'type': 'Person',
            'id': self.ap_id(),
            'name': self.name,
            'preferredUsername': self.name,
            'summary': 'my simple activitypub',
            'inbox': settings.SERVER_URL+'/'+self.name+'/inbox',
            'outbox': settings.SERVER_URL+'/'+self.name+'/outbox',
            'url': settings.SERVER_URL+'/'+self.name,
            'icon': {
                '@context': 'https://www.w3.org/ns/activitystreams',
                'type': 'Image',
                'mediaType': self.mimetype_from_path(settings.MEDIA_ROOT+'/'+self.icon.name),
                'url': settings.SERVER_URL+self.icon.url,
            },
            'publicKey': self.key_to_dict(),
        }

class Follower(BaseModel):
    followings = models.ManyToManyField(Account)
    name       = models.CharField(max_length=255, default='')
    domain     = models.CharField(max_length=255, default='')
    ap_id      = models.CharField(max_length=255, default='')
    inbox      = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.name+'@'+self.domain

class Note(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField(max_length=500, default='')
    url     = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.content

    def save(self, *args, **kwargs):
        super(Note, self).save(*args, **kwargs)

    def contentHtml(self):
        return '<p>'+self.content+'<br /><a href="'+self.url+' target="_blank">'+self.url+'</a></p>'

    def ap_id(self):
        return self.account.ap_id()+'/'+str(self.id)

    def to_dict(self):
        return {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'type': 'Note',
            'id': self.ap_id(),
            'attributedTo': self.account.ap_id(),
            'content': self.contentHtml(),
            'published': self.created_at.isoformat(),
            'to': [
                'https://www.w3.org/ns/activitystreams#Public',
                self.account.ap_id()+'/followers',
            ],
        }

    def post(self):
        for follower in self.account.follower_set.all():
            to = follower.inbox
            jsn = {
                '@context': 'https://www.w3.org/ns/activitystreams',
                'type': 'Create',
                'object': self.to_dict(),
            }
            headers = sign_headers(self.account, 'POST', urlparse(to).path)
            response = requests.post(to, json=jsn, headers=headers)
            if response.status_code >= 400 and response.status_code < 600:
                print("note post error")

class Attachment(BaseModel):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='attachments')
    url = models.TextField(max_length=255, default='')
