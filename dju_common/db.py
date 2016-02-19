# coding=utf-8
import gc
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


def chunked_qs(qs, order_by='pk', chunksize=1000, yield_values=True):
    qs = qs.order_by(order_by)
    if order_by.startswith('-'):
        fn = 'lt'
        ord_field = order_by[1:]
    else:
        fn = 'gt'
        ord_field = order_by
    last_ordered_val = None
    empty = False
    while not empty:
        empty = True
        chunk_qs = qs
        if last_ordered_val is not None:
            chunk_qs = chunk_qs.filter(**{'{}__{}'.format(ord_field, fn): last_ordered_val})
        chunk_qs = chunk_qs[:chunksize]
        if yield_values:
            row = None
            for row in chunk_qs:
                yield row
            if row is not None:
                last_ordered_val = getattr(row, ord_field)
                empty = False
        else:
            rows = tuple(chunk_qs)
            yield rows
            if rows:
                last_ordered_val = getattr(rows[-1], ord_field)
                empty = False
        gc.collect()


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
