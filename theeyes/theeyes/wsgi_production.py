import os
import sys
import site
# Add path to site-packages in our virtualenv
site.addsitedir("/srv/theeyes/venv/lib/python3.4/site-packages")

from django.core.wsgi import get_wsgi_application
sys.path = ['/srv/theeyes/theeyes'] + sys.path
os.environ['DJANGO_SETTINGS_MODULE'] = 'theeyes.settings.production'
application = get_wsgi_application()
