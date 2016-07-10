from __future__ import absolute_import
from django.utils.text import capfirst
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


def mt_modelform_field_restore_original_label(field, make_capfirst=False):
    """
    If label of field has suffix with language, you can fix it, for example:

    class MyModelForm(models.ModelForm):
        class Meta:
            model = MyModel
            _mt_fields = mt_fields(('title', 'description'), nomaster=True)
            fields = _mt_fields

        def __init__(self, *args, **kwargs):
            super(ItemCategoryEditForm, self).__init__(*args, **kwargs)

            for field_name in self.Meta._mt_fields:
                mt_modelform_field_restore_original_label(self.fields[field_name], make_capfirst=True)
    """
    field.label = field.label._proxy____args[0]._proxy____args[0]
    if make_capfirst:
        field.label = capfirst(field.label)


def mt_modelform_register_clean_method(form_self, field_name, func, nomaster=False):
    """
    You can add clean_<field_name> for each translated field. For example:

    class MyModelForm(models.ModelForm):
        class Meta:
            model = MyModel
            _mt_fields = mt_fields(('title', 'description'), nomaster=True)
            fields = _mt_fields

        def __init__(self, *args, **kwargs):
            super(ItemCategoryEditForm, self).__init__(*args, **kwargs)

            mt_modelform_register_clean_method(self, 'title', self.mt_clean_title, nomaster=True)

        def mt_clean_title(self, field_name, lang):
            value = self.cleaned_data[field_name]
            # validation here
            return value
    """
    args_list = [('{}_{}'.format(field_name, lang), lang) for lang in AVAILABLE_LANGUAGES]
    if not nomaster:
        args_list.append((field_name, None))

    def _get_mt_clean_method(args):
        def _mt_clean_method():
            return func(*args)
        return _mt_clean_method

    for item_args in args_list:
        method_name = 'clean_{}'.format(item_args[0])
        setattr(form_self, method_name, _get_mt_clean_method(item_args))
