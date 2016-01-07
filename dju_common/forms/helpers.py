def add_css_class_to_field(form_field, css_class):
    attrs = form_field.widget.attrs
    if 'class' in attrs:
        if attrs['class']:
            attrs['class'] += ' '
    else:
        attrs['class'] = ''
    attrs['class'] += css_class
