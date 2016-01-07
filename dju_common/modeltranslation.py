from __future__ import absolute_import
from modeltranslation.settings import AVAILABLE_LANGUAGES


def mt_fields(*fields):
    """
    Returns list of fields for multilanguage fields of model.
    Examples:
        print mt_fields('name', 'desc')
        ['name', 'name_en', 'name_uk', 'desc', 'desc_en', 'desc_uk']

        MyModel.objects.only(*mt_fields('name', 'desc', 'content'))
    """
    fl = []
    for field in fields:
        fl.append(field)
        for lang in AVAILABLE_LANGUAGES:
            fl.append('{}_{}'.format(field, lang))
    return fl
