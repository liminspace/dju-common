import time
from django.http import QueryDict
from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase


class TestTemplatetagsCommon(TestCase):
    class R(object):
        def __init__(self, query):
            self.GET = QueryDict(query)

    def get_tpl_f(self, tpl, context=None):
        return lambda: Template('{% load dju_tcache %}' + tpl).render(Context(context))

    def test_tcache(self):

        def get_content():
            get_content.n += 1
            return get_content.n
        get_content.n = -1

        t = self.get_tpl_f("{% tcache 1 test0 tags='foo,bar' %}{{ var }}{% endtcache %}", {'var': get_content})
        self.assertEqual(t(), '0')
        self.assertEqual(t(), '0')
        self.assertEqual(t(), '0')
        time.sleep(1)
        self.assertEqual(t(), '1')

        t = self.get_tpl_f(
            "{% tcache 1 test1 'a' 1 b tags='foo,bar' %}{{ var }}{% endtcache %}",
            {'var': get_content, 'b': 2}
        )
        self.assertEqual(t(), '2')
        self.assertEqual(t(), '2')
        self.assertEqual(t(), '2')
        time.sleep(1)
        self.assertEqual(t(), '3')

        t = self.get_tpl_f(
            "{% tcache 1 test2 tags=var2 %}{{ var }}{% endtcache %}",
            {'var': get_content, 'var2': {'a': 1}}
        )
        self.assertRaises(TemplateSyntaxError, t)

        t = self.get_tpl_f(
            "{% tcache a test3 tags=var2 %}{{ var }}{% endtcache %}",
            {'var': get_content, 'var2': ['foo', 'bar']}
        )
        self.assertRaises(TemplateSyntaxError, t)

        t = self.get_tpl_f(
            "{% tcache 1 %}{{ var }}{% endtcache %}",
            {'var': get_content, 'var2': ['foo', 'bar']}
        )
        self.assertRaises(TemplateSyntaxError, t)
