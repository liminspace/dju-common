from __future__ import absolute_import
from django import template
from dju_common import gravatar


register = template.Library()


@register.filter
def gravatar_ava_url(email, size=None):
    return gravatar.get_ava_url(email, size=size)


@register.filter
def gravatar_profile_url(value):
    return gravatar.get_profile_url(value)
