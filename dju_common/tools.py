# coding=utf-8
import os
import re
import time
import pytz
import datetime
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from . import settings as dju_settings


def natural_sorted(iterable, key=None, cmp_func=None, reverse=False):
    reg = re.compile(r'([0-9]+)')
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    if key is None:
        key = lambda t: t
    alphanum_key = lambda val: [convert(c) for c in reg.split(key(val))]
    return sorted(iterable, key=alphanum_key, cmp=cmp_func, reverse=reverse)


def int2base36(n):
    """
    Convert int base10 to base36.
    Back convert: int('<base36>', 36)
    """
    assert isinstance(n, (int, long))
    c = '0123456789abcdefghijklmnopqrstuvwxyz'
    if n < 0:
        return '-' + int2base36(-n)
    elif n < 36:
        return c[n]
    b36 = ''
    while n != 0:
        n, i = divmod(n, 36)
        b36 = c[i] + b36
    return b36


def datetime_to_dtstr(dt=None):
    """
    Comvert datetime to short text.
    If datetime has timezone then it will be convert to UTC0.
    """
    if dt is None:
        dt = datetime.datetime.utcnow()
    elif timezone.is_aware(dt):
        dt = dt.astimezone(tz=pytz.UTC)
    return int2base36(int(time.mktime(dt.timetuple()) * 1e3 + dt.microsecond / 1e3))


def dtstr_to_datetime(dtstr, to_tz=None, fail_silently=True):
    """
    Convert result from datetime_to_dtstr to datetime in timezone UTC0.
    """
    try:
        dt = datetime.datetime.utcfromtimestamp(int(dtstr, 36) / 1e3)
        if to_tz:
            dt = timezone.make_aware(dt, timezone=pytz.UTC)
            if to_tz != pytz.UTC:
                dt = dt.astimezone(to_tz)
        return dt
    except ValueError, e:
        if not fail_silently:
            raise e
        return None


def load_object_by_name(obj_name):
    """
    Import object by name (point-path).
    Example:
        MyForm = load_object_by_name('myapp.forms.MyAnyForm')
    """
    parts = obj_name.split('.')
    t = __import__('.'.join(parts[:-1]), fromlist=(parts[-1],))
    return getattr(t, parts[-1])

    
def parse_datetime_aware(s, tz=None):
    """
    Parse text with datetime to aware datetime (with timezone).
    """
    assert settings.USE_TZ
    if isinstance(s, datetime.datetime):
        return s
    d = parse_datetime(s)
    if d is None:
        raise ValueError
    return timezone.make_aware(d, tz or timezone.get_current_timezone())


_long_number_readable_formats = (
    (10 ** 6, 10 ** 3, u'{:.0f}', u'{:.1f}', _(u'k.')),
    (10 ** 9, 10 ** 6, u'{:.0f}', u'{:.2f}', _(u' mln.')),
    (10 ** 12, 10 ** 9, u'{:.0f}', u'{:.3f}', _(u' bln.')),
)


def long_number_readable(value):
    """
    Convert big int (>=999) to readable form.
    1000 => 1k.
    2333 => 2.3k.
    1000000 => 1 mln.
    1258000 => 1.26 mln.
    """
    value = int(value)
    if value < 1000:
        return value
    for m, d, inf, fnf, n in _long_number_readable_formats:
        if value < m:
            return ((inf if value % d == 0 else fnf) + unicode(n)).format(value / float(d))
    return value


def log_to_file(msg, double_br=False, add_time=True, fn=None):
    fn = fn or os.path.join(settings.LOG_DIR, 'log_to_file.log').replace('\\', '/')
    with open(fn, 'a') as f:
        msg += '\n' * (int(bool(double_br)) + 1)
        if add_time:
            msg = u'[{}] {}'.format(datetime.datetime.now().strftime(u'%d.%m.%Y %H:%M:%S'), msg)
        f.write(msg.encode('utf8'))


def log_memory_usage(desc='test'):
    try:
        import psutil
    except ImportError:
        raise ImportError("Can't import psutil. Please, install psutil (pip install psutil).")
    proc = psutil.Process(os.getpid())
    mem = proc.get_memory_info()[0] / float(2 ** 20)
    log_to_file('{}: {} MB'.format(desc, mem), add_time=False,
                fn=os.path.join(dju_settings.LOG_DIR, 'memory_usage.log').replace('\\', '/'))
