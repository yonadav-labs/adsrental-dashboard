import os

import pymysql
from django.core.wsgi import get_wsgi_application

from config.environment import SETTINGS_MODULE
print "test"

pymysql.install_as_MySQLdb()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
application = get_wsgi_application()
app = application
