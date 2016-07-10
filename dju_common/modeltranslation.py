from __future__ import absolute_import
from modeltranslation.settings import AVAILABLE_LANGUAGES, DEFAULT_LANGUAGE


def mt_fields(fields, nomaster=False, onlydefaultlang=False):
    """
    Returns list of fields for multilanguage fields of model.
    Examples:
        print mt_fields('name', 'desc')
        ['name', 'name_en', 'name_uk', 'desc', 'desc_en', 'desc_uk']

        MyModel.objects.only(*mt_fields('name', 'desc', 'content'))

    If nomaster then master field will not be append.
    F.e.: ['name_en', 'name_uk'] -- without master 'name'.

    If onlydefaultlang then wiil be search only default language:
    F.e.: ['name', 'name_en'] -- without additional 'name_uk'.

    If nomaster and onlydefaultlang then will be use both rulses.
    F.e.: ['name_en'] -- without master 'name' and additional 'name_uk'.
    """
    assert isinstance(fields, (list, tuple))
    fl = []
    for field in fields:
        if not nomaster:
            fl.append(field)
        if onlydefaultlang:
            fl.append('{}_{}'.format(field, DEFAULT_LANGUAGE))
        else:
            for lang in AVAILABLE_LANGUAGES:
                fl.append('{}_{}'.format(field, lang))
    return fl
