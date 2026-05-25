import os
env = os.environ.get('DJANGO_SETTINGS_MODULE', '')
if not env:
    from .dev import *
