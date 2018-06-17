#!/usr/bin/env python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simple_ap.settings")
from activitypub.apps import app

if __name__ == "__main__":
    app.run()
