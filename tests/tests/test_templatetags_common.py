try:
    from html import unescape  # python 3.4+
except ImportError:
    from HTMLParser import HTMLParser  # python 2.x
    unescape = HTMLParser().unescape

from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.http import QueryDict
from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase
from django.utils.html import escape
from dju_common import settings as dju_settings


class TestTemplatetagsCommon(TestCase):
    class R(object):
        def __init__(self, query):
            self.GET = QueryDict(query)

    def get_tpl_f(self, tpl, context=None):
        return lambda: Template('{% load dju_common %}' + tpl).render(Context(context))

    def test_of_key(self):
        t = self.get_tpl_f("{{ var|of_key:'a' }}", {'var': {'a': 1}})
        self.assertEqual(t(), '1')

        t = self.get_tpl_f("{{ var|of_key:1 }}", {'var': {1: 2}})
        self.assertEqual(t(), '2')

        t = self.get_tpl_f("{{ var|of_key:'1' }}", {'var': {1: 2}})
        self.assertEqual(t(), '')

        t = self.get_tpl_f("{{ var|of_key:'a' }}", {'var': [1, 2, 3]})
        self.assertEqual(t(), '')

    def test_of_strkey(self):
        t = self.get_tpl_f("{{ var|of_strkey:1 }}", {'var': {'1': 2}})
        self.assertEqual(t(), '2')

        t = self.get_tpl_f("{{ var|of_strkey:1 }}", {'var': [1, 2, 3]})
        self.assertEqual(t(), '')

    def test_of_intkey(self):
        t = self.get_tpl_f("{{ var|of_intkey:2 }}", {'var': [1, 2, 3, 4]})
        self.assertEqual(t(), '3')

        t = self.get_tpl_f("{{ var|of_intkey:'2' }}", {'var': [1, 2, 3, 4]})
        self.assertEqual(t(), '3')

        t = self.get_tpl_f("{{ var|of_intkey:9 }}", {'var': [1, 2, 3, 4]})
        self.assertEqual(t(), '')

    def test_is_in(self):
        t = self.get_tpl_f("{{ var|is_in:'a|b|c' }}", {'var': 'b'})
        self.assertEqual(t(), 'True')

        t = self.get_tpl_f("{{ var|is_in:'a|b|c' }}", {'var': 'z'})
        self.assertEqual(t(), 'False')

        t = self.get_tpl_f("{{ var|is_in:var2 }}", {'var': 2, 'var2': [1, 2, 3]})
        self.assertEqual(t(), 'True')

        t = self.get_tpl_f("{{ var|is_in:var2 }}", {'var': 9, 'var2': [1, 2, 3]})
        self.assertEqual(t(), 'False')

    def test_captureas(self):
        t = self.get_tpl_f('{% captureas t %}content{% endcaptureas %}{{ t }}')
        self.assertEqual(t(), 'content')

        t = self.get_tpl_f('{% captureas t 1 %}content{% endcaptureas %}{{ t }}')
        self.assertEqual(t(), 'contentcontent')

        t = self.get_tpl_f('{% captureas t 1 2 %}content{% endcaptureas %}{{ t }}')
        self.assertRaises(TemplateSyntaxError, t)

        t = self.get_tpl_f('{% captureas %}content{% endcaptureas %}{{ t }}')
        self.assertRaises(TemplateSyntaxError, t)

    def test_strip(self):
        t = self.get_tpl_f('{% strip %} content \n \n content \n {% endstrip %}')
        self.assertEqual(t(), 'content content')

        t = self.get_tpl_f("{% strip '' %} content \n \n content \n {% endstrip %}")
        self.assertEqual(t(), 'contentcontent')

        t = self.get_tpl_f("{% strip '{\\n}' %} content \n \n content \n {% endstrip %}")
        self.assertEqual(t(), 'content\ncontent')

        t = self.get_tpl_f("{% strip '<br>' %} content \n \n content \n {% endstrip %}")
        self.assertEqual(t(), 'content<br>content')

        t = self.get_tpl_f("{% strip '' 1 %} content \n \n content \n {% endstrip %}{{ t }}")
        self.assertRaises(TemplateSyntaxError, t)

    def test_include_silently(self):
        t = self.get_tpl_f("{% include_silently 'not_exists_tpl.html' %}", {'var': 'test'})
        self.assertEqual(t().strip(), '')

        t = self.get_tpl_f("{% include_silently 'exists_tpl.html' %}", {'var': 'test'})
        self.assertEqual(t().strip(), 'test')

        t = self.get_tpl_f("{% include_silently %}")
        self.assertRaises(TemplateSyntaxError, t)

        t = self.get_tpl_f("{% include_silently 1 2 %}")
        self.assertRaises(TemplateSyntaxError, t)

    def test_recurse(self):
        t = self.get_tpl_f('''{% strip '' %}[
                {% recurse var %}
                    {{ recurse_level }}
                    {{ item.name }}
                    {% if item.children %}
                        [{{ subitems }}]
                    {% endif %}
                {% endrecurse %}
            ]{% endstrip %}''',
            {'var': [
                {'name': 'a', 'children': [
                    {'name': 'b', 'children': [
                        {'name': 'c'},
                        {'name': 'd'}
                    ]},
                    {'name': 'e'},
                ]}
            ]}
        )
        self.assertEqual(t(), '[1a[2b[3c3d]2e]]')

        t = self.get_tpl_f('''{% strip '' %}[
                {% recurse var 'subitems' %}
                    {{ recurse_level }}
                    {{ item.name }}
                    {% if item.subitems %}
                        [{{ subitems }}]
                    {% endif %}
                {% endrecurse %}
            ]{% endstrip %}''',
            {'var': [
                {'name': 'a', 'subitems': [
                    {'name': 'b', 'subitems': lambda: [
                        {'name': 'c'},
                        {'name': 'd'}
                    ]},
                    {'name': 'e'},
                ]}
            ]}
        )
        self.assertEqual(t(), '[1a[2b[3c3d]2e]]')

        class TreeItem(object):
            def __init__(self, name, children=None):
                self.name = name
                self._children = None
                if children:
                    assert isinstance(children, (list, tuple))
                    self._children = children

            def children(self):
                return self._children

        t = self.get_tpl_f('''{% strip '' %}[
                {% recurse var %}
                    {{ recurse_level }}
                    {{ item.name }}
                    {% if item.children %}
                        [{{ subitems }}]
                    {% endif %}
                {% endrecurse %}
            ]{% endstrip %}''',
            {'var': [
                TreeItem('a', [
                    TreeItem('b', [
                        TreeItem('c'),
                        TreeItem('d'),
                    ]),
                    TreeItem('e'),
                ])
            ]}
        )
        self.assertEqual(t(), '[1a[2b[3c3d]2e]]')

        t = self.get_tpl_f('{% recurse %}{% endstrip %}')
        self.assertRaises(TemplateSyntaxError, t)

        t = self.get_tpl_f('{% recurse a b %}{% endstrip %}')
        self.assertRaises(TemplateSyntaxError, t)

    def test_humanize_long_number(self):
        t = self.get_tpl_f('{{ var|humanize_long_number }}', {'var': 555})
        self.assertEqual(t(), '555')

        t = self.get_tpl_f('{{ var|humanize_long_number }}', {'var': 1000})
        self.assertEqual(t(), '1k.')

        t = self.get_tpl_f('{{ var|humanize_long_number }}', {'var': 2333})
        self.assertEqual(t(), '2.3k.')

        t = self.get_tpl_f('{{ var|humanize_long_number }}', {'var': 1000000})
        self.assertEqual(t(), '1 mln.')

        t = self.get_tpl_f('{{ var|humanize_long_number }}', {'var': 1258000})
        self.assertEqual(t(), '1.26 mln.')

        t = self.get_tpl_f('{{ var|humanize_long_number }}', {'var': 1258000000})
        self.assertEqual(t(), '1.258 bln.')

        t = self.get_tpl_f('{{ var|humanize_long_number }}', {'var': 12580000000000})
        self.assertEqual(t(), '12580000000000')

        t = self.get_tpl_f('{{ var|humanize_long_number }}', {'var': 100.5555})
        self.assertEqual(t(), '100')

    def test_int_subtract(self):
        t = self.get_tpl_f("{{ var|int_subtract:'10' }}", {'var': 100})
        self.assertEqual(t(), '90')

        t = self.get_tpl_f("{{ var|int_subtract:'a' }}", {'var': 100})
        self.assertEqual(t(), '')

        t = self.get_tpl_f("{{ var|int_subtract:'10' }}", {'var': 'a'})
        self.assertEqual(t(), '')

    def test_assign(self):
        t = self.get_tpl_f("{% assign 'abc' as v %}{{ v }}")
        self.assertEqual(t(), 'abc')

    def test_assign_default(self):
        t = self.get_tpl_f("{% assign_default 'v' 'default' %}{{ v }}")
        self.assertEqual(t(), 'default')

        t = self.get_tpl_f("{% assign_default 'v' 'default' %}{{ v }}", {'v': 'value'})
        self.assertEqual(t(), 'value')

    def test_assign_format_str(self):
        t = self.get_tpl_f("{% assign_format_str 'a_{:.1f}' 1 as v %}{{ v }}")
        self.assertEqual(t(), 'a_1.0')

        t = self.get_tpl_f("{% assign_format_str 'a_{b:.1f}' b=1 as v %}{{ v }}")
        self.assertEqual(t(), 'a_1.0')

    def test_tojson(self):
        t = self.get_tpl_f("{{ var|tojson }}", {'var': [{'a': 1}, {'b': [2, 3]}]})
        self.assertEqual(t(), escape('[{"a": 1}, {"b": [2, 3]}]'))

    def test_paginator(self):
        paginator = Paginator(tuple(xrange(50)), 10)

        t = self.get_tpl_f('{% paginator var %}', {'var': paginator.page(1)})
        self.assertEqual(t(), (
            '<li class="disabled">prev</li>'
            '<li class="active"><a href="?page=1">1</a></li>'
            '<li><a href="?page=2">2</a></li>'
            '<li><a href="?page=3">3</a></li>'
            '<li><a href="?page=4">4</a></li>'
            '<li><a href="?page=5">5</a></li>'
            '<li><a href="?page=2">next</a></li>'
        ))

        t = self.get_tpl_f('{% paginator var %}', {'var': paginator.page(3)})
        self.assertEqual(t(), (
            '<li><a href="?page=2">prev</a></li>'
            '<li><a href="?page=1">1</a></li>'
            '<li><a href="?page=2">2</a></li>'
            '<li class="active"><a href="?page=3">3</a></li>'
            '<li><a href="?page=4">4</a></li>'
            '<li><a href="?page=5">5</a></li>'
            '<li><a href="?page=4">next</a></li>'
        ))

        t = self.get_tpl_f('{% paginator var %}', {'var': paginator.page(5)})
        self.assertEqual(t(), (
            '<li><a href="?page=4">prev</a></li>'
            '<li><a href="?page=1">1</a></li>'
            '<li><a href="?page=2">2</a></li>'
            '<li><a href="?page=3">3</a></li>'
            '<li><a href="?page=4">4</a></li>'
            '<li class="active"><a href="?page=5">5</a></li>'
            '<li class="disabled">next</li>'
        ))

        paginator = Paginator(tuple(xrange(500)), 10)

        t = self.get_tpl_f('{% paginator var %}', {'var': paginator.page(1)})
        self.assertEqual(t(), (
            '<li class="disabled">prev</li>'
            '<li class="active"><a href="?page=1">1</a></li>'
            '<li><a href="?page=2">2</a></li>'
            '<li><a href="?page=3">3</a></li>'
            '<li><a href="?page=4">4</a></li>'
            '<li><a href="?page=5">5</a></li>'
            '<li><a href="?page=6">6</a></li>'
            '<li><a href="?page=7">7</a></li>'
            '<li><a href="?page=8">8</a></li>'
            '<li class="disabled">...</li>'
            '<li><a href="?page=48">48</a></li>'
            '<li><a href="?page=49">49</a></li>'
            '<li><a href="?page=50">50</a></li>'
            '<li><a href="?page=2">next</a></li>'
        ))

        t = self.get_tpl_f('{% paginator var %}', {'var': paginator.page(25)})
        self.assertEqual(t(), (
            '<li><a href="?page=24">prev</a></li>'
            '<li><a href="?page=1">1</a></li>'
            '<li><a href="?page=2">2</a></li>'
            '<li><a href="?page=3">3</a></li>'
            '<li class="disabled">...</li>'
            '<li><a href="?page=22">22</a></li>'
            '<li><a href="?page=23">23</a></li>'
            '<li><a href="?page=24">24</a></li>'
            '<li class="active"><a href="?page=25">25</a></li>'
            '<li><a href="?page=26">26</a></li>'
            '<li><a href="?page=27">27</a></li>'
            '<li><a href="?page=28">28</a></li>'
            '<li class="disabled">...</li>'
            '<li><a href="?page=48">48</a></li>'
            '<li><a href="?page=49">49</a></li>'
            '<li><a href="?page=50">50</a></li>'
            '<li><a href="?page=26">next</a></li>'
        ))

        t = self.get_tpl_f('{% paginator var %}', {'var': paginator.page(50)})
        self.assertEqual(t(), (
            '<li><a href="?page=49">prev</a></li>'
            '<li><a href="?page=1">1</a></li>'
            '<li><a href="?page=2">2</a></li>'
            '<li><a href="?page=3">3</a></li>'
            '<li class="disabled">...</li>'
            '<li><a href="?page=43">43</a></li>'
            '<li><a href="?page=44">44</a></li>'
            '<li><a href="?page=45">45</a></li>'
            '<li><a href="?page=46">46</a></li>'
            '<li><a href="?page=47">47</a></li>'
            '<li><a href="?page=48">48</a></li>'
            '<li><a href="?page=49">49</a></li>'
            '<li class="active"><a href="?page=50">50</a></li>'
            '<li class="disabled">next</li>'
        ))

    def test_str_equal(self):
        t = self.get_tpl_f("{{ var|str_equal:'1' }}", {'var': 1})
        self.assertEqual(t(), 'True')

        t = self.get_tpl_f("{{ var|str_equal:'1' }}", {'var': 2})
        self.assertEqual(t(), 'False')

        t = self.get_tpl_f("{{ var|str_equal:'aaa' }}", {'var': 'aaa'})
        self.assertEqual(t(), 'True')

        t = self.get_tpl_f("{{ var|str_equal:'aaa' }}", {'var': 'bbb'})
        self.assertEqual(t(), 'False')

        t = self.get_tpl_f("{{ var|str_equal:var2 }}", {'var': 'aaa', 'var2': 'aaa'})
        self.assertEqual(t(), 'True')

        t = self.get_tpl_f("{{ var|str_equal:var2 }}", {'var': 'aaa', 'var2': 'bbb'})
        self.assertEqual(t(), 'False')

    def test_html_encode(self):
        t = self.get_tpl_f('{{ var|html_encode }}', {'var': 'mailto:my@site.com'})
        self.assertEqual(t(), '&#109;&#97;&#105;&#108;&#116;&#111;&#58;'
                              '&#109;&#121;&#64;&#115;&#105;&#116;&#101;&#46;&#99;&#111;&#109;')

    def test_url_getvars(self):
        t = self.get_tpl_f('{% url_getvars %}', {'request': self.R('a=1&b=2&b=3')})
        self.assertEqual(QueryDict(unescape(t())), QueryDict('a=1&b=2&b=3'))

    def test_url_getvars_with(self):
        t = self.get_tpl_f("{% url_getvars_with 'b,c' %}", {'request': self.R('a=1&b=2&b=3&c=4')})
        self.assertEqual(QueryDict(unescape(t())), QueryDict('b=2&b=3&c=4'))

        t = self.get_tpl_f("{% url_getvars_with '&b,c' %}", {'request': self.R('a=1&b=2&b=3&c=4')})
        self.assertTrue(t().startswith('&'))

        t = self.get_tpl_f("{% url_getvars_with 'b,c&' %}", {'request': self.R('a=1&b=2&b=3&c=4')})
        self.assertTrue(unescape(t()).endswith('&'))

        t = self.get_tpl_f("{% url_getvars_with '&b,c&' %}", {'request': self.R('a=1&b=2&b=3&c=4')})
        self.assertTrue(unescape(t()).startswith('&') and unescape(t()).endswith('&'))

        t = self.get_tpl_f("{% url_getvars_with '' %}", {'request': self.R('a=1&b=2&b=3')})
        self.assertEqual(t(), '')

    def test_url_getvars_without(self):
        t = self.get_tpl_f("{% url_getvars_without 'a,c' %}", {'request': self.R('a=1&b=2&b=3&c=4')})
        self.assertEqual(QueryDict(unescape(t())), QueryDict('b=2&b=3'))

        t = self.get_tpl_f("{% url_getvars_without '' %}", {'request': self.R('a=1&b=2&b=3&c=4')})
        self.assertEqual(QueryDict(unescape(t())), QueryDict('a=1&b=2&b=3&c=4'))

    def test_full_url_prefix(self):
        r = '{scheme}://' + Site.objects.get_current().domain

        t = self.get_tpl_f('{% full_url_prefix %}')
        self.assertEqual(t(), r.format(scheme=(dju_settings.USE_HTTPS and 'https' or 'http')))

        t = self.get_tpl_f('{% full_url_prefix 0 %}')
        self.assertEqual(t(), r.format(scheme='http'))

        t = self.get_tpl_f('{% full_url_prefix 1 %}')
        self.assertEqual(t(), r.format(scheme='https'))

    def test_add_full_url_prefix(self):
        r = '{scheme}://' + Site.objects.get_current().domain

        t = self.get_tpl_f('{{ var|add_full_url_prefix }}', {'var': '/test.html'})
        self.assertEqual(t(), r.format(scheme=(dju_settings.USE_HTTPS and 'https' or 'http')) + '/test.html')

        t = self.get_tpl_f('{{ var|add_full_url_prefix:0 }}', {'var': '/test.html'})
        self.assertEqual(t(), r.format(scheme='http') + '/test.html')

        t = self.get_tpl_f('{{ var|add_full_url_prefix:1 }}', {'var': '/test.html'})
        self.assertEqual(t(), r.format(scheme='https') + '/test.html')
