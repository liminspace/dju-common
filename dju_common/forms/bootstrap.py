from django import forms
from .helpers import add_css_class_to_fields_widget


BS_FORM_WIDGETS = (forms.TextInput, forms.Textarea, forms.Select, forms.FileInput)


class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        add_css_class_to_fields_widget(self.fields, 'form-control')


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        add_css_class_to_fields_widget(self.fields, 'form-control')
