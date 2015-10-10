import urllib
import hashlib
from . import settings as dju_settings


def get_ava_url(email, size=None):
    if not size:
        size = dju_settings.DJU_GRAVATAR_DEFAULT_SIZE
    return '{}://www.gravatar.com/avatar/{}?{}'.format(
        (dju_settings.DJU_GRAVATAR_SECURE and 'https' or 'http'),
        hashlib.md5(email.lower()).hexdigest(),
        urllib.urlencode({
            'd': dju_settings.DJU_GRAVATAR_DEFAULT_IMAGE,
            's': str(size),
            'r': dju_settings.DJU_GRAVATAR_RATING
        })
    )


def get_profile_url(email):
    return '{}://ru.gravatar.com/{}'.format(
        (dju_settings.DJU_GRAVATAR_SECURE and 'https' or 'http'),
        hashlib.md5(email.lower()).hexdigest()
    )
