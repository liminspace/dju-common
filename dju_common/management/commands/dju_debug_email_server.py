import codecs
import sys
import os
import base64
import re
import datetime
import subprocess
import traceback
from smtpd import SMTPServer
from django.core.management.base import BaseCommand
from django.utils.encoding import force_unicode, force_str
from dju_common.settings import DJU_EMAIL_DEBUG_PATH, DJU_EMAIL_DEBUG_IN_CONSOLE, DJU_EMAIL_DEBUG_IN_FILES


class DebuggingServer(SMTPServer):
    def __init__(self, *args, **kwargs):
        SMTPServer.__init__(self, *args, **kwargs)
        sys.stdout = codecs.getwriter('utf8')(sys.stdout)
        sys.stderr = codecs.getwriter('utf8')(sys.stderr)
        print 'Debug email server is running. Now you can send emails to SMTP localhost:10250.'

    @staticmethod
    def _get_subject(data):
        subject_re = re.compile(ur'^Subject: (.+)$', re.IGNORECASE | re.U)
        base64_re = re.compile(ur'^=\?(.+)\?b\?(.+)\?=$', re.IGNORECASE | re.U)
        for line in data.split('\n'):
            m = subject_re.match(line)
            if m:
                subject = m.group(1).strip()
                m = base64_re.match(subject)
                if m:
                    charset, content = m.groups()
                    subject = force_unicode(base64.b64decode(content))
                return subject
        return ''

    @staticmethod
    def _get_fn(fn_base, n=None):
        if n is None:
            return os.path.join(DJU_EMAIL_DEBUG_PATH, '{}.eml'.format(fn_base)).replace('\\', '/')
        else:
            return os.path.join(DJU_EMAIL_DEBUG_PATH, '{}_{}.eml'.format(fn_base, n)).replace('\\', '/')

    def process_message(self, peer, mailfrom, rcpttos, data):
        try:
            if DJU_EMAIL_DEBUG_IN_FILES:
                if not os.path.exists(DJU_EMAIL_DEBUG_PATH):
                    os.makedirs(DJU_EMAIL_DEBUG_PATH)
                fn_base = u'{}_{}_{}_{}'.format(
                    u'_'.join(rcpttos),
                    self._get_subject(data),
                    mailfrom,
                    datetime.datetime.now().strftime(u'%Y-%m-%d_%H-%M-%S')
                )
                fn_base = re.sub(ur'[:\*\?"<>\| ]+', '_', fn_base, re.U)
                fn_base = force_str(fn_base)
                fn = self._get_fn(fn_base)
                n = 1
                while os.path.exists(fn):
                    fn = self._get_fn(fn_base, n)
                    n += 1
                f = codecs.open(fn, 'w', encoding='utf-8')
            inheaders = 1
            for line in data.split('\n'):
                if inheaders and not line:
                    if DJU_EMAIL_DEBUG_IN_FILES:
                        f.write(u'X-Peer: {}\n'.format(force_unicode(peer[0])))
                    if DJU_EMAIL_DEBUG_IN_CONSOLE:
                        print u'X-Peer: {}'.format(force_unicode(peer[0]))
                    inheaders = 0
                line = force_unicode(line)
                if DJU_EMAIL_DEBUG_IN_FILES:
                    f.write(u'{}\n'.format(line))
                if DJU_EMAIL_DEBUG_IN_CONSOLE:
                    print line
        except Exception, e:
            traceback.print_exc()
            print 'DebuggingServer error: {}'.format(force_unicode(e))


class Command(BaseCommand):
    help = 'Run debug smtp server'

    def handle(self, *args, **options):
        env = os.environ.copy()
        env['PYTHONPATH'] = os.pathsep.join(sys.path)
        if os.name == 'nt':
            for k in env:
                env[k] = env[k].encode('utf-8')
        subprocess.call([
            sys.executable,
            '-m', 'smtpd', '-n', '-c', 'dju_common.management.commands.dju_debug_email_server.DebuggingServer',
            'localhost:10250'
        ], env=env)
