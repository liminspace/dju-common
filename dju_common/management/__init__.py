import datetime
import inspect
import os
from django.conf import settings
from django.core.management import BaseCommand
from django.utils.encoding import force_unicode
from dju_common import settings as dju_settings


class LoggingBaseCommand(BaseCommand):
    log_fn = None
    log_err_fn = None
    log_dir = dju_settings.LOG_DIR
    log_out_enabled = settings.DEBUG
    log_err_out_enabled = settings.DEBUG

    def log(self, msg, add_time=True, out=None, double_br=False, ending=None, std_stream=None, is_error=False):
        if std_stream is None:
            std_stream = self.stdout
        if out is None:
            out = self.log_out_enabled
        msg = force_unicode(msg, errors='replace')
        if double_br:
            msg += '\n\n'
        if add_time:
            msg = u'[%s] %s' % (datetime.datetime.now().strftime(u'%d.%m.%Y %H:%M:%S'), msg)
        if out:
            std_stream.write(msg, ending=ending)
        with open(os.path.join(self.log_dir, self.get_log_fn(is_error=is_error)).replace('\\', '/'), 'a') as f:
            f_ending = '\n' if ending is None else ending
            if f_ending and not msg.endswith(f_ending):
                msg += f_ending
            f.write(msg.encode('utf8'))

    def log_err(self, msg, add_time=True, out=None, double_br=False, ending=None, std_stream=None):
        if std_stream is None:
            std_stream = self.stderr
        if out is None:
            out = self.log_err_out_enabled
        self.log(msg, add_time=add_time, out=out, double_br=double_br, ending=ending, std_stream=std_stream,
                 is_error=True)

    def get_log_fn(self, is_error=False):
        get_cmd_name = lambda: os.path.splitext(os.path.basename(inspect.getfile(self.__class__)))[0]
        if is_error:
            if self.log_err_fn is None:
                return '{}.error.log'.format(get_cmd_name())
            return self.log_err_fn
        else:
            if self.log_fn is None:
                return '{}.log'.format(get_cmd_name())
            return self.log_fn
