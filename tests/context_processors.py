from django.contrib.sites.models import Site
from dju_common.http import full_url


def static(request=None):
    return {
        'STATIC_CP_VALUE': 'STATIC_CP_VALUE_OK',
        'SITE': Site.objects.get_current,
        'HOMEPAGE_URL': full_url,
    }
