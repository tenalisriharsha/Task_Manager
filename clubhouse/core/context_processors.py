# File: core/context_processors.py
from .models import SiteSetting

def site_settings(request):
    return {'SITE': SiteSetting.get_solo()}
