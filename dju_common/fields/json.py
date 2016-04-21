import copy
import datetime
import simplejson
from types import NoneType
from django.db import models
from django.forms.widgets import Textarea
from django.utils.timezone import is_aware
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import CharField
from django.forms.utils import ValidationError


JSON_INVALID = ValidationError(_('Enter valid JSON.'))


class JSONFormField(CharField):
    def __init__(self, *args, **kwargs):
        self.load_kwargs = kwargs.pop('load_kwargs', {})
        self.dump_kwargs = kwargs.pop('dump_kwargs', {})
        super(JSONFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value and not self.required:
            return None
        if isinstance(value, basestring):
            try:
                value = simplejson.loads(value, **self.load_kwargs)
            except ValueError:
                raise JSON_INVALID
        return value

    def prepare_value(self, value):
        if isinstance(value, basestring):
            value = simplejson.loads(value, **self.load_kwargs)
        kwargs = self.dump_kwargs.copy()
        kwargs['sort_keys'] = True
        if isinstance(self.widget, Textarea):
            kwargs['indent'] = 4
        return simplejson.dumps(value, **kwargs)


class JSONEncoder(simplejson.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date, time, datetime.
    """
    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError(_("JSON can't represent timezone-aware times."))
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        else:
            return super(JSONEncoder, self).default(o)


class JSONFieldBase(models.Field):
    DEFAULT_SEPARATORS = (',', ':')

    def __init__(self, *args, **kwargs):
        if 'default' not in kwargs:
            kwargs['default'] = None
        elif not isinstance(kwargs['default'], (list, dict, NoneType)) and not callable(kwargs['default']):
            raise AssertionError('Default can be None, list or dict.')
        if 'blank' not in kwargs:
            kwargs['blank'] = True
        use_decimal = kwargs.pop('use_decimal', False)
        self.dump_kwargs = {'cls': JSONEncoder,
                            'separators': self.DEFAULT_SEPARATORS,
                            'use_decimal': use_decimal}
        self.dump_kwargs.update(kwargs.pop('dump_kwargs', {}))
        self.load_kwargs = {'use_decimal': use_decimal}
        self.load_kwargs.update(kwargs.pop('load_kwargs', {}))
        super(JSONFieldBase, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, basestring):
            if value == '':
                return None
            try:
                return simplejson.loads(value, **self.load_kwargs)
            except ValueError:
                raise JSON_INVALID
        return value

    def from_db_value(self, value, expression, connection, context):
        if value in (None, ''):
            return None
        return simplejson.loads(value, **self.load_kwargs)

    def get_prep_value(self, value):
        if value is None and self.null:
            return None
        return simplejson.dumps(value, **self.dump_kwargs)

    def get_default(self):
        return self.default() if callable(self.default) else copy.deepcopy(self.default)

    def formfield(self, **kwargs):
        if 'form_class' not in kwargs:
            kwargs['form_class'] = JSONFormField
        field = super(JSONFieldBase, self).formfield(**kwargs)
        if not field.help_text:
            field.help_text = _('JSON data')
        if isinstance(field, JSONFormField):
            field.load_kwargs = self.load_kwargs
            field.dump_kwargs = self.dump_kwargs
        return field

    def deconstruct(self):
        name, path, args, kwargs = super(JSONFieldBase, self).deconstruct()
        kwargs['dump_kwargs'] = self.dump_kwargs
        kwargs['load_kwargs'] = self.load_kwargs
        return name, path, args, kwargs


class JSONField(JSONFieldBase, models.TextField):
    pass


class JSONCharField(JSONFieldBase, models.CharField):
    pass
