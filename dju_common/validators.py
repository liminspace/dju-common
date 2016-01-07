from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from . import settings as dju_settings


def validate_email_domain(email):
    """ Validates email domain by blacklist. """
    try:
        domain = email.split('@', 1)[1].lower().strip()
    except IndexError:
        return
    if domain in dju_settings.DJU_EMAIL_DOMAIN_BLACK_LIST:
        raise ValidationError(_(u'Email with domain "%(domain)s" is disallowed.'),
                              code='banned_domain', params={'domain': domain})
