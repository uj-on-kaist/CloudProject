import os
import sys
import os.path

yourpath = os.path.abspath(os.path.dirname(__file__))
path = os.path.abspath(os.path.join(yourpath, '..'))
path2 = os.path.abspath(os.path.join(os.path.join(yourpath, '..'), '..'))
if path not in sys.path:
    sys.path.append(path)
if path2 not in sys.path:
    sys.path.append(path2)

os.environ['DJANGO_SETTINGS_MODULE'] = 'Cloud31.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

