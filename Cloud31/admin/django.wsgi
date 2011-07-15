import os
import sys
import os.path

yourpath = os.path.abspath(os.path.dirname(__file__))
path = os.path.abspath(os.path.join(yourpath, '..'))
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'Cloud31.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
