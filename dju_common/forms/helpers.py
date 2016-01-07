from django import forms


DEFAULT_VISIBLE_WIDGETS = (forms.TextInput, forms.Textarea, forms.Select, forms.FileInput)


def add_css_class_to_fields_widget(form_fields, css_class, widget_types=DEFAULT_VISIBLE_WIDGETS):
    for k in form_fields:
        if isinstance(form_fields[k].widget, widget_types):
            add_css_class_to_field(form_fields[k], css_class)


def add_css_class_to_field(form_field, css_class):
    attrs = form_field.widget.attrs
    if 'class' in attrs:
        if attrs['class']:
            attrs['class'] += ' '
    else:
        attrs['class'] = ''
    attrs['class'] += css_class
