from django import forms
from .helpers import add_css_class_to_field


BS_FORM_WIDGETS = (forms.TextInput, forms.Textarea, forms.Select, forms.FileInput)


def add_css_class_to_fields_widget(form_fields, css_class, widget_types=BS_FORM_WIDGETS):
    for k in form_fields:
        if isinstance(form_fields[k].widget, widget_types):
            add_css_class_to_field(form_fields[k], css_class)


class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        add_css_class_to_fields_widget(self.fields, 'form-control')


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        add_css_class_to_fields_widget(self.fields, 'form-control')
