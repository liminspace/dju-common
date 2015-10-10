from django.http import QueryDict
from django.template import Template, Context
from django.test import TestCase
from dju_common import settings as dju_settings


class TestTemplatetagsCommon(TestCase):
    class R(object):
        def __init__(self, query):
            self.GET = QueryDict(query)

    def get_tpl_f(self, tpl, context=None):
        return lambda: Template('{% load dju_gravatar %}' + tpl).render(Context(context))


    def test_gravatar_ava_url(self):
        r = '{scheme}://www.gravatar.com/avatar/903e415f53009aef5c2c3c1330ec74da?s={s}&amp;r={r}&amp;d={d}'
        scheme = (dju_settings.DJU_GRAVATAR_SECURE and 'https' or 'http')

        t = self.get_tpl_f('{{ var|gravatar_ava_url }}', {'var': 'liminspace@gmail.com'})
        self.assertEqual(t(), r.format(scheme=scheme, s=dju_settings.DJU_GRAVATAR_DEFAULT_SIZE,
                                       r=dju_settings.DJU_GRAVATAR_RATING, d=dju_settings.DJU_GRAVATAR_DEFAULT_IMAGE))

        t = self.get_tpl_f('{{ var|gravatar_ava_url:100 }}', {'var': 'liminspace@gmail.com'})
        self.assertEqual(t(), r.format(scheme=scheme, s=100, r=dju_settings.DJU_GRAVATAR_RATING,
                                       d=dju_settings.DJU_GRAVATAR_DEFAULT_IMAGE))

    def test_gravatar_profile_url(self):
        t = self.get_tpl_f('{{ var|gravatar_profile_url }}', {'var': 'liminspace@gmail.com'})
        self.assertEqual(t(), 'http://ru.gravatar.com/903e415f53009aef5c2c3c1330ec74da')
