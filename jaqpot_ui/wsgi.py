"""
WSGI config for jaqpot_ui project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jaqpot_ui.settings")

# sys.path.append(os.path.join(os.environ['/'], 'wsgi',
#     'jaqpot_ui'))
# os.path.join(os.environ['OPENSHIFT_HOMEDIR'], 'app-root/repo')


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
