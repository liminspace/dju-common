import simplejson
import datetime
import pytz
from django.utils.dateparse import parse_datetime, parse_date, parse_time
from django.utils.timezone import is_aware


# todo cover tests


class JSONEncoder(simplejson.JSONEncoder):
    @staticmethod
    def custom_obj(custom_type, data):
        return {'@_type_': custom_type, '@_data_': data}

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            if is_aware(o):
                o = o.astimezone(pytz.utc)
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            return self.custom_obj('datetime', r)
        elif isinstance(o, datetime.date):
            return self.custom_obj('date', o.isoformat())
        elif isinstance(o, datetime.time):
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return self.custom_obj('time', r)
        else:
            return super(JSONEncoder, self).default(o)


class JSONSerializer(object):
    @classmethod
    def object_hook(cls, d):
        s = d.get('@_data_')
        if s:
            dt = d.get('@_type_')
            if dt == 'datetime':
                return parse_datetime(s)
            elif dt == 'date':
                return parse_date(s)
            elif dt == 'time':
                return parse_time(s)
        return d

    @classmethod
    def dumps(cls, obj):
        return simplejson.dumps(obj, cls=JSONEncoder, separators=(',', ':'))

    @classmethod
    def loads(cls, data):
        return simplejson.loads(data, use_decimal=True, object_hook=cls.object_hook)
