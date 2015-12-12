# coding=utf-8
from django.shortcuts import _get_queryset


def get_object_or_None(klass, *args, **kwargs):
    """
    Uses get() to return an object or None if the object does not exist.
    klass may be a Model, Manager, or QuerySet object.
    All other passed arguments and keyword arguments are used in the get() query.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def chunked_qs(qs, chunksize=1000, yield_values=True):
    start = 0
    while True:
        empty = True
        if yield_values:
            for t in qs[start:(start + chunksize)]:
                yield t
                empty = False
        else:
            data = tuple(qs[start:(start + chunksize)])
            yield data
            if data:
                empty = False
        if empty:
            break
        start += chunksize


def chunked_qs_by_field(qs, fieldname, chunksize=1000):
    """
    Буде зроблено кілька запитів, які будуть пагінуватись з допомогою фільтру
    по числовому полю fieldname (значенням від 0 шматками chunksize)
    """
    start = 0
    while True:
        empty = True
        f = {'{f}__gte'.format(f=fieldname): start, '{f}__lt'.format(f=fieldname): start + chunksize}
        for t in qs.filter(**f):
            yield t
            empty = False
        if empty:
            break
        start += chunksize


def each_fields(for_fields, fields):
    """
    select_related(
        'field__related_field1__text1', 'field__related_field1__text2',
        'field__related_field2__text1', 'field__related_field2__text2',
    )
    select_related(*each_fields(['field__related_field1', 'field__related_field2'], ['text1', 'text2']))
    each_fields('field__related_field1', ['text1', 'text2'])
    """
    if isinstance(for_fields, basestring):
        for_fields = (for_fields,)
    r = set()
    for ff in for_fields:
        for f in fields:
            r.add(ff + '__' + f)
    return list(r)
