from __future__ import absolute_import
import simplejson
from django import template
from django.template.loader import get_template
from django.http import QueryDict
from django.utils.safestring import mark_safe, mark_for_escaping
from django.utils.encoding import force_unicode
from dju_common.http import full_url
from dju_common.tools import long_number_readable


register = template.Library()


@register.filter
def of_key(var, key):
    try:
        return var[key]
    except (KeyError, TypeError, IndexError):
        return ''


@register.filter
def of_intkey(var, key):
    try:
        return var[int(key)]
    except (KeyError, TypeError, IndexError):
        return ''


@register.filter
def of_strkey(var, key):
    try:
        return var[str(key)]
    except (KeyError, TypeError):
        return ''


@register.filter
def is_in(val, items):
    """
    {% if tag|is_in:'div|p|span' %}is block tag{% endif %}
    {% if tag|is_in:tags_list %}is block tag{% endif %}
    """
    if isinstance(items, basestring):
        items = items.split('|')
    return val in items


class CaptureasNode(template.Node):
    def __init__(self, nodelist, args):
        self.nodelist = nodelist
        self.varname = args[1]
        self.assign_and_print = len(args) > 2 and bool(args[2])

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return output if self.assign_and_print else ''


@register.tag
def captureas(parser, arg):
    """
    example: {% captureas myvar 1 %}content...{% endcaptureas %} - {{ myvar }}
    result: content... - content...

    example: {% captureas myvar %}content...{% endcaptureas %} - {{ myvar }}
    result: - content...
    """
    args = arg.contents.split()
    if not 2 <= len(args) <= 3:
        raise template.TemplateSyntaxError('"captureas" node requires a variable name and/or assign only')
    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()
    return CaptureasNode(nodelist, args)


class StripNode(template.Node):
    def __init__(self, nodelist, args):
        if len(args) > 2:
            raise template.TemplateSyntaxError("'%s' tag can have one parameter" % args[0])
        self.nodelist = nodelist
        self.separator = args[1][1:-1] if len(args) == 2 else ' '
        self.separator = self.separator.replace('{\\n}', '\n')

    def render(self, context):
        output = self.nodelist.render(context)
        return self.separator.join(filter(bool, [line.strip() for line in output.splitlines()]))


@register.tag
def strip(parser, arg):
    """
    example:
        {% strip '<br>' %}
            content...
            content...
        {% endstrip %}
    result:
        content...<br>content...
    arg special symbols: {\n} = \n
    """
    nodelist = parser.parse(('endstrip',))
    parser.delete_first_token()
    return StripNode(nodelist, arg.split_contents())


class IncludeNode(template.Node):
    def __init__(self, template_name):
        self.template_name = template_name

    def render(self, context):
        try:
            try:
                included_template = context.template.engine.get_template(self.template_name).render(context)
            except AttributeError:
                included_template = get_template(self.template_name).render(context)
        except template.TemplateDoesNotExist:
            included_template = ''
        return included_template


@register.tag
def include_silently(parser, token):
    """
    Include template if it exists.
    If it doesn't exist then will not raise any exception.
    {% include_silently "mytemplate.html" %}
    """
    try:
        tag_name, template_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires a single argument' % token.contents.split()[0])
    return IncludeNode(template_name[1:-1])


class RecurseNode(template.Node):
    def __init__(self, template_nodes, items_var, children_attr):
        self.template_nodes = template_nodes
        self.items_var = items_var
        self.children_attr = children_attr

    def _render(self, context, item, level=1):
        t = []
        context.push()
        children = ()
        if hasattr(item, self.children_attr):
            children = getattr(item, self.children_attr, ())
            if callable(children):
                children = children()
        elif hasattr(item, 'get'):
            children = item.get(self.children_attr, ())
            if callable(children):
                children = children()
        for child in children or ():
            t.append(self._render(context, child, level=level + 1))
        context['item'] = item
        context['subitems'] = mark_safe(''.join(t))
        context['recurse_level'] = level
        rendered = self.template_nodes.render(context)
        context.pop()
        return rendered

    def render(self, context):
        return ''.join(self._render(context, item) for item in self.items_var.resolve(context))


@register.tag
def recurse(parser, token):
    """
    Iterate recurse data structure.
    <ul>
        {% recurse items %}
            <li>
                {{ item.name }}
                {% if item.children %}
                    <ul>
                        {{ subitems }}
                    </ul>
                {% endif %}
            </li>
        {% endrecurse %}
    </ul>
    If subelements found in other key/attribute/method then need set its name (default is 'children'):
        {% recurse items 'subitems' %}
    Also available depth level in variable {{ recurse_level }} (starting of 1)
    """
    params = token.contents.split()
    if not 2 <= len(params) <= 3:
        raise template.TemplateSyntaxError('%s parameters error' % params[0])
    template_nodes = parser.parse(('endrecurse',))
    parser.delete_first_token()
    return RecurseNode(template_nodes,
                       template.Variable(params[1]),
                       (params[2][1:-1] if len(params) == 3 else 'children'))


@register.filter
def humanize_long_number(value):
    """
    Convert big integer (>=999) to readable form.
    """
    return long_number_readable(value)

    
@register.filter
def int_subtract(a, b):
    """
    Subtract the arg of the value.
    """
    try:
        return int(a) - int(b)
    except (ValueError, TypeError):
        return ''


@register.simple_tag
def assign(value):
    """
    Setting value to a variable.
    {% assign obj.get_full_name as obj_full_name %}
    """
    return value


@register.simple_tag(takes_context=True)
def assign_default(context, var_name, default):
    """
    Sets default value to variable if one does not exist.
    """
    if var_name not in context:
        context[var_name] = default
    return ''


@register.simple_tag
def assign_format_str(string, *args, **kwargs):
    """
    Format string and save it to variable.
    {% assign_format_str 'contacts_{lang}.html' lang=LANGUAGE_CODE as tpl_name %}
    {% include tpl_name %}
    """
    return string.format(*args, **kwargs)


@register.filter
def tojson(value):
    """
    Convert value to json-object.
        var data = '{{ data|tojson|safe }}';
        <div data-data="{{ data|tojson }}"></div>
    """
    return simplejson.dumps(value)


@register.inclusion_tag(('paginator.html', 'dju_common/tags/paginator.html'), takes_context=True)
def paginator(context, page, leading=8, out=3, adjacent=3, sep='...'):
    """
    Render paginator.
    <<_1_2 3 4 5 6 7 8 9 ... 55 56 57 >>  # leading=9 (1..9)  out=3 (55..57)
    << 1 2 3 ... 23 24 25 26_27_28 29 30 31 ... 55 56 57 >>  # adjacent = 4 (23..26, 28..31)
    """
    leading_pages, out_left_pages, out_right_pages, pages = [], [], [], []
    num_pages = page.paginator.num_pages
    is_paginated = num_pages > 1
    if is_paginated:
        if num_pages < leading:
            leading_pages = [x for x in xrange(1, leading) if x <= num_pages]
        elif page.number <= leading - 1:
            leading_pages = [x for x in xrange(1, leading + 1)]
            out_right_pages = [x + num_pages for x in xrange(-out + 1, 1) if x + num_pages > leading]
        elif page.number > num_pages - leading + 1:
            leading_pages = [x for x in xrange(num_pages - leading + 1, num_pages + 1) if x <= num_pages]
            out_left_pages = [x for x in xrange(1, out + 1) if num_pages - x >= leading]
        else:
            leading_pages = [x for x in xrange(page.number - adjacent, page.number + adjacent + 1)]
            out_right_pages = [x + num_pages for x in xrange(-out + 1, 1)]
            out_left_pages = [x for x in xrange(1, out + 1)]
    if out_left_pages:
        pages.extend(out_left_pages)
        pages.append(sep)
    pages.extend(leading_pages)
    if out_right_pages:
        pages.append(sep)
        pages.extend(out_right_pages)
    return {
        'page': page,
        'pages': pages,
        'is_paginated': is_paginated,
        'separator': sep,
        'request': context.get('request'),
        'param_name': page.param_name if hasattr(page, 'param_name') else 'page',
    }


@register.filter
def str_equal(a, b):
    return force_unicode(a) == force_unicode(b)


@register.filter
def html_encode(value):
    """
    Encode text to HTML special symbols.
    Example:
        <a href="{{ 'mailto:my@example.com'|html_encode }}">{{ 'my@example.com'|html_encode }}</a>
    Result:
        <a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;&#109;&#121;&#64;...">&#109;&#121;&#64;&#101;&#120;...</a>
    """
    return mark_safe(''.join('&#%d;' % ord(c) for c in value))


def _url_get_amps(token=None):
    l, r, amp = '', '', '&'
    if token and len(token) > 1:
        token = token.strip()
        if token.startswith('&'):
            l = amp
        if token.endswith('&'):
            r = amp
        token = token.strip('&')
    return token, l, r


def _url_getvars(context, token_=None, type_=None):
    assert type_ in (None, 'with', 'without')
    request_get = getattr(context.get('request'), 'GET', QueryDict(''))
    token, l, r = _url_get_amps(token_)
    gv = ''
    if type_:
        w, wo = type_ == 'with', type_ == 'without'
        if w or wo:
            lst = [p.strip() for p in token.split(',') if p.strip()]
            if w and not lst:
                pass
            elif wo and not lst:
                type_ = None
            else:
                params = QueryDict('', mutable=True)
                if w:
                    q = lambda x: x
                else:
                    q = lambda x: not x
                for key in request_get:
                    if q(key in lst):
                        params.setlist(key, request_get.getlist(key))
                gv = params.urlencode()
    if not type_:
        gv = request_get.urlencode()
    if gv:
        gv = l + gv + r
    return gv


@register.simple_tag(takes_context=True)
def url_getvars(context, token=None):
    return mark_for_escaping(_url_getvars(context, token))


@register.simple_tag(takes_context=True)
def url_getvars_with(context, token):
    return mark_for_escaping(_url_getvars(context, token, 'with'))


@register.simple_tag(takes_context=True)
def url_getvars_without(context, token):
    return mark_for_escaping(_url_getvars(context, token, 'without'))


@register.simple_tag
def full_url_prefix(secure=None):
    return full_url(secure=secure)


@register.filter
def add_full_url_prefix(value, arg=None):
    return mark_safe(full_url(path=value, secure=arg))
