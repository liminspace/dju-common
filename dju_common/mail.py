import copy
import re
from django.core.mail import EmailMultiAlternatives
from django.template import RequestContext
from django.template import loader, Context
from django.template.loader import render_to_string
from django.template.loader_tags import BlockNode, ExtendsNode
from django.conf import settings
from django.utils import translation, timezone
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _
from . import settings as dju_settings


def attach_html_wrapper(content, title=None, head=None):
    return render_to_string('dju_common/mail/html_wrapper.html', {'content': content, 'title': title, 'head': head})


def send_mail(subject, body, to, from_email=None, reply_to=None,
              fail_silently=False, attach_alternative=None, attaches=None):
    headers = {}
    if dju_settings.DJU_EMAIL_RETURN_PATH:
        headers['Return-Path'] = dju_settings.DJU_EMAIL_RETURN_PATH
    if settings.EMAIL_SUBJECT_PREFIX:
        subject = _(settings.EMAIL_SUBJECT_PREFIX) + subject
    if isinstance(to, basestring):
        to = (to,)
    if reply_to is None:
        reply_to = dju_settings.DJU_EMAIL_REPLY_TO or None
    if isinstance(reply_to, basestring):
        reply_to = [reply_to]
    mail = EmailMultiAlternatives(subject=subject, body=body, from_email=from_email, to=to, headers=headers,
                                  reply_to=reply_to)
    if attach_alternative:
        for attach in attach_alternative:
            mail.attach_alternative(*attach)
    if attaches:
        for attach in attaches:
            mail.attach(*attach)
    return mail.send(fail_silently)


class RenderMailSender(object):
    TEMPLATE_EXT = '.html'

    class TemplateNodeNotFound(Exception):
        pass

    def __init__(self, tpl_fn, context=None, request=None, from_email=None, reply_to=None,
                 fail_silently=False, attach_alternative=None, attaches=None, lang=None, tz=None):
        self._tpl_fn = None
        self._context = None
        self._request = None
        self._from_email = None
        self._reply_to = None
        self._fail_silently = None
        self._attach_alternative = None
        self._attaches = None
        self._lang = None
        self._tz = None
        self._allow_configs = ('tpl_fn', 'context', 'request', 'from_email', 'reply_to', 'fail_silently',
                               'attach_alternative', 'attaches', 'lang', 'tz')
        self.configure(tpl_fn=tpl_fn, context=context, request=request, from_email=from_email, reply_to=reply_to,
                       fail_silently=fail_silently, attach_alternative=attach_alternative, attaches=attaches,
                       lang=lang, tz=tz)
        self._tpl = None
        self._context_instance = None
        self._lang_old = None
        self._tz_old = None
        self._render_cache = {}

    def configure(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k not in self._allow_configs:
                raise AttributeError('Unknown attr "%s"' % k)
            setattr(self, '_' + k, v)
            if k in ('tpl_fn', 'lang'):
                self._tpl = None
                self._render_cache = {}
            elif k in ('request', 'context'):
                self._context_instance = None
                self._render_cache = {}

    def _load_tpl(self):
        if self._tpl is None:
            self._tpl = loader.select_template((
                '{fn}_{lang}{ext}'.format(fn=self._tpl_fn, lang=translation.get_language(), ext=self.TEMPLATE_EXT),
                '{fn}{ext}'.format(fn=self._tpl_fn, ext=self.TEMPLATE_EXT),
                self._tpl_fn,
            ))

    def _create_context_instance(self):
        if self._context_instance is None:
            if self._request:
                self._context_instance = RequestContext(self._request)
            else:
                dc = dju_settings.DJU_EMAIL_DEFAULT_CONTEXT
                self._context_instance = Context(
                    import_string(dc)() if dc else None
                )
            if self._context:
                self._context_instance.update(self._context)

    def _render_template_block(self, name, nodes=None, extended_blocks=None, context_instance=None):
        if nodes is None:
            nodes = self._tpl.template.nodelist
        if extended_blocks is None:
            extended_blocks = {}
        for node in nodes:
            if isinstance(node, BlockNode) and node.name == name:
                for i, n in enumerate(node.nodelist):
                    if isinstance(n, BlockNode) and n.name in extended_blocks:
                        node.nodelist[i] = extended_blocks[n.name]
                return node.render(context_instance)
            if hasattr(node, 'nodelist'):
                try:
                    return self._render_template_block(name, nodes=node.nodelist, extended_blocks=extended_blocks,
                                                       context_instance=context_instance)
                except self.TemplateNodeNotFound:
                    pass
            if isinstance(node, ExtendsNode):
                eb = dict((n.name, n) for n in node.nodelist if isinstance(n, BlockNode))
                eb.update(extended_blocks)
                try:
                    return self._render_template_block(name, nodes=node.get_parent(context_instance),
                                                       extended_blocks=eb, context_instance=context_instance)
                except self.TemplateNodeNotFound:
                    pass
        raise self.TemplateNodeNotFound('Block "%s" not found.' % name)

    def _render(self, name):
        if name not in self._render_cache:
            if self._context_instance is not None:
                with self._context_instance.bind_template(self._tpl.template):
                    self._render_cache[name] = self._render_template_block(
                            name, context_instance=copy.deepcopy(self._context_instance)
                    ).strip()
            else:
                self._render_cache[name] = self._render_template_block(
                        name, context_instance=Context()
                ).strip()
        return self._render_cache[name]

    @classmethod
    def _plain_normalize(cls, plain):
        r = re.compile(r'^` (.+)')
        plain = '\n'.join(r.sub(r'  \1', line.strip()) for line in plain.replace('\r', '').split('\n'))
        plain = re.sub(r'\n{3,}', '\n\n', plain)
        return plain

    def _set_locale(self):
        self._lang_old = translation.get_language()
        self._tz_old = timezone.get_current_timezone_name()
        if self._lang and self._lang != self._lang_old:
            translation.activate(self._lang)
        else:
            self._lang_old = None
        if self._tz and self._tz != self._tz_old:
            timezone.activate(self._tz)
        else:
            self._tz_old = None

    def _back_locale(self):
        if self._lang_old:
            translation.activate(self._lang_old)
        if self._tz_old:
            timezone.activate(self._tz_old)

    def send(self, to):
        if not isinstance(to, (list, tuple)):
            to = (to,)
        self._set_locale()
        try:
            self._load_tpl()
            self._create_context_instance()
            attach_alternative = tuple(self._attach_alternative) if self._attach_alternative else ()
            attach_alternative += ((self._render('html'), 'text/html'),)
            return send_mail(self._render('subject'), self._plain_normalize(self._render('plain')), to,
                             from_email=self._from_email, reply_to=self._reply_to, fail_silently=self._fail_silently,
                             attach_alternative=attach_alternative, attaches=self._attaches)
        finally:
            self._back_locale()
