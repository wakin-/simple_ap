import feedparser
import pandas
import django
django.setup()
from activitypub.models import Account, Note

def get_feeds_from_url(url):
    feed = feedparser.parse(url)
    return pandas.DataFrame(feed.entries)

def get_new_feeds(account):
    feeds = get_feeds_from_url(account.feed_url)
    note_ids = Note.objects.filter(account=account).values_list('url', flat=True)
    return feeds[~feeds['id'].isin(list(note_ids))]

def run():
    accounts = Account.objects.all()
    for account in accounts:
        new_feeds = get_new_feeds(account)
        if not new_feeds.empty:
            for key, row in new_feeds.iterrows():
                note = Note(account=account, content=row['title'], url=row['id'])
                note.save()
                print('new feed:'+row['title'])
                note.post()
