import os
import sys

path = '/home/rogeriodev81/bookstore-docker2'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'bookstore.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
