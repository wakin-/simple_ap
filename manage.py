#!/usr/bin/env python
import os
import sys

def exec_django():
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simple_ap.settings")
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        from activitypub.apps import app as api
        api.run()
    elif len(sys.argv) > 1 and sys.argv[1] == "rss":
        import rss_importer as rss
        rss.run()
    else:
        exec_django()
