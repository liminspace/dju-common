import os
from django.conf import settings


# ------------
# COMMON SETTINGS
# ------------
LOG_DIR = getattr(settings, 'LOG_DIR', os.path.join(settings.BASE_DIR, 'logs').replace('\\', '/'))
USE_HTTPS = getattr(settings, 'USE_HTTPS', False)


# ------------
# SENDING EMAIL
# ------------
DJU_EMAIL_RETURN_PATH = getattr(settings, 'DJU_EMAIL_RETURN_PATH', None)
DJU_EMAIL_REPLY_TO = getattr(settings, 'DJU_EMAIL_REPLY_TO', None)  # list of emails
DJU_EMAIL_DOMAIN_BLACK_LIST = getattr(settings, 'DJU_EMAIL_DOMAIN_BLACK_LIST', (
    'mailinator.com', '10minutemail.com', 'spambog.com', 'tempinbox.com', 'mailmetrash.com',
    'tempemail.net', 'yopmail.com', 'sharklasers.com', 'guerrillamailblock.com', 'guerrillamail.com',
    'guerrillamail.net', 'guerrillamail.biz', 'guerrillamail.org', 'guerrillamail.de', 'spam4.me', 'spam.su',
    'inboxed.im', 'inboxed.pw', 'gomail.in', 'tokem.co', 'nomail.pw', 'yanet.me', 'powered.name', 'shut.ws',
    'vipmail.pw', 'powered.im', 'linuxmail.so', 'secmail.pw', 'shut.name', 'freemail.ms', 'mailforspam.com',
    'uroid.com', 'rmqkr.net',
))
DJU_EMAIL_DEFAULT_CONTEXT = getattr(settings, 'DJU_EMAIL_DEFAULT_CONTEXT',
                                    'dju_common.context_processors.email_default')


# ------------
# EMAIL DEBUGGING
# ------------
DJU_EMAIL_DEBUG_IN_CONSOLE = getattr(settings, 'DJU_EMAIL_DEBUG_IN_CONSOLE', True)
DJU_EMAIL_DEBUG_IN_FILES = getattr(settings, 'DJU_EMAIL_DEBUG_IN_FILES', True)
DJU_EMAIL_DEBUG_PATH = getattr(settings, 'DJU_EMAIL_DEBUG_PATH',
                               os.path.join(LOG_DIR, 'debug_email').replace('\\', '/'))


# ------------
# GRAVATAR
# ------------
DJU_GRAVATAR_DEFAULT_SIZE = getattr(settings, 'DJU_GRAVATAR_DEFAULT_SIZE', 50)
# 404, mm, identicon, monsterid, wavatar, retro, blank, http://mysite.com/default.jpg
DJU_GRAVATAR_DEFAULT_IMAGE = getattr(settings, 'DJU_GRAVATAR_DEFAULT_IMAGE', 'mm')
DJU_GRAVATAR_RATING = getattr(settings, 'DJU_GRAVATAR_RATING', 'g')  # g, pg, r, x
DJU_GRAVATAR_SECURE = getattr(settings, 'DJU_GRAVATAR_SECURE', USE_HTTPS)
