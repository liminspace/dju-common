import copy
import re
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import translation, timezone
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _
from .constants import DJU_EMAIL_BLOCK_MARKERS
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
    BLOCKS_RE = {
        'subject': re.compile(r'{}(.*?){}'.format(*DJU_EMAIL_BLOCK_MARKERS['subject']), re.U | re.S),
        'plain_body': re.compile(r'{}(.*?){}'.format(*DJU_EMAIL_BLOCK_MARKERS['plain_body']), re.U | re.S),
        'html_body': re.compile(r'{}(.*?){}'.format(*DJU_EMAIL_BLOCK_MARKERS['html_body']), re.U | re.S),
    }

    class TemplateEmailTagNotFound(Exception):
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
        self._lang_old = None
        self._tz_old = None
        self._render_cache = None
        self._context_cache = None

    def configure(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k not in self._allow_configs:
                raise AttributeError('Unknown attr "%s"' % k)
            setattr(self, '_' + k, v)
            if k in ('tpl_fn', 'lang', 'tz'):
                self._tpl = None
                self._render_cache = None
            elif k in ('request', 'context'):
                self._context_cache = None
                self._render_cache = None

    def _get_tpl(self):
        if self._tpl is None:
            self._tpl = loader.select_template((
                '{fn}_{lang}{ext}'.format(fn=self._tpl_fn, lang=translation.get_language(), ext=self.TEMPLATE_EXT),
                '{fn}{ext}'.format(fn=self._tpl_fn, ext=self.TEMPLATE_EXT),
                self._tpl_fn,
            ))
        return self._tpl

    def _get_context(self):
        if self._context_cache is None:
            self._context_cache = {} if self._context is None else copy.copy(self._context)
            if not self._request:
                if dju_settings.DJU_EMAIL_DEFAULT_CONTEXT:
                    self._context_cache.update(import_string(dju_settings.DJU_EMAIL_DEFAULT_CONTEXT)())
        return self._context_cache

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
            if self._render_cache is None:
                tpl = self._get_tpl()
                r = tpl.render(context=self._get_context(), request=self._request)
                for block, markers in DJU_EMAIL_BLOCK_MARKERS.iteritems():
                    for marker in markers:
                        if marker not in r:
                            raise self.TemplateEmailTagNotFound('Require tag not used: dju_email_{}.'.format(block))
                contents = {
                    'subject': self.BLOCKS_RE['subject'].search(r).group(1).strip(),
                    'plain_body': self._plain_normalize(self.BLOCKS_RE['plain_body'].search(r).group(1).strip()),
                    'html_body': self.BLOCKS_RE['html_body'].search(r).group(1).strip(),
                }
                self._render_cache = contents
                del r
            else:
                contents = self._render_cache
            attach_alternative = tuple(self._attach_alternative) if self._attach_alternative else ()
            if contents['html_body']:
                attach_alternative += ((contents['html_body'], 'text/html'),)
            return send_mail(contents['subject'], contents['plain_body'], to,
                             from_email=self._from_email, reply_to=self._reply_to, fail_silently=self._fail_silently,
                             attach_alternative=attach_alternative, attaches=self._attaches)
        finally:
            self._back_locale()
