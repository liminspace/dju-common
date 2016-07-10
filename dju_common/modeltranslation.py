from __future__ import absolute_import
from modeltranslation.settings import AVAILABLE_LANGUAGES, DEFAULT_LANGUAGE


def mt_fields(nomaster__=False, onlydefaultlang__=False, *fields):
    """
    Returns list of fields for multilanguage fields of model.
    Examples:
        print mt_fields('name', 'desc')
        ['name', 'name_en', 'name_uk', 'desc', 'desc_en', 'desc_uk']

        MyModel.objects.only(*mt_fields('name', 'desc', 'content'))

    If nomaster__ then master field will not be append.
    F.e.: ['name_en', 'name_uk'] -- without master 'name'.

    If onlydefaultlang__ then wiil be search only default language:
    F.e.: ['name', 'name_en'] -- without additional 'name_uk'.

    If nomaster__ and onlydefaultlang__ then will be use both rulses.
    F.e.: ['name_en'] -- without master 'name' and additional 'name_uk'.
    """
    fl = []
    for field in fields:
        if not nomaster__:
            fl.append(field)
        if onlydefaultlang__:
            fl.append('{}_{}'.format(field, DEFAULT_LANGUAGE))
        else:
            for lang in AVAILABLE_LANGUAGES:
                fl.append('{}_{}'.format(field, lang))
    return fl
