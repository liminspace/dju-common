from __future__ import absolute_import
from django import template
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache
from dju_common.tcache import cache_set


register = template.Library()


class CacheNode(template.Node):
    def __init__(self, nodelist, expire_time_var, fragment_name, vary_on, tags):
        self.nodelist = nodelist
        self.expire_time_var = expire_time_var
        self.fragment_name = fragment_name
        self.vary_on = vary_on
        self.tags = tags

    def get_tags(self, context):
        if self.tags:
            tags = self.tags.resolve(context)
            if isinstance(tags, basestring):
                tags = [tag.strip() for tag in tags.split(',')]
            elif not isinstance(tags, (list, tuple, set)):
                raise template.TemplateSyntaxError('"tcache" tag variable "tags" invalid')
            return filter(None, tags) or None

    def render(self, context):
        try:
            expire_time = self.expire_time_var.resolve(context)
            expire_time = int(expire_time)
        except (ValueError, TypeError):
            raise template.TemplateSyntaxError('"tcache" tag got a non-integer timeout value: %r' % expire_time)
        vary_on = [var.resolve(context) for var in self.vary_on]
        cache_key = make_template_fragment_key(self.fragment_name, vary_on)
        value = cache.get(cache_key)
        if value is None:
            value = self.nodelist.render(context)
            cache_set(cache_key, value, timeout=expire_time, tags=self.get_tags(context))
        return value


@register.tag
def tcache(parser, token):
    """
    This will cache the contents of a template fragment for a given amount
    of time with support tags.

    Usage::
        {% tcache [expire_time] [fragment_name] [tags='tag1,tag2'] %}
            .. some expensive processing ..
        {% endtcache %}

    This tag also supports varying by a list of arguments:
        {% tcache [expire_time] [fragment_name] [var1] [var2] .. [tags=tags] %}
            .. some expensive processing ..
        {% endtcache %}

    Each unique set of arguments will result in a unique cache entry.
    """
    nodelist = parser.parse(('endtcache',))
    parser.delete_first_token()
    tokens = token.split_contents()
    if len(tokens) < 3:
        raise template.TemplateSyntaxError("'%r' tag requires at least 2 arguments." % tokens[0])
    tags = None
    if len(tokens) > 3 and 'tags=' in tokens[-1]:
        tags = parser.compile_filter(tokens[-1][5:])
        del tokens[-1]
    return CacheNode(nodelist,
        parser.compile_filter(tokens[1]),
        tokens[2],  # fragment_name can't be a variable.
        [parser.compile_filter(token) for token in tokens[3:]],
        tags
    )
