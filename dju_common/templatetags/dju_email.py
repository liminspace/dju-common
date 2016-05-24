from django import template
from ..constants import DJU_EMAIL_BLOCK_MARKERS


register = template.Library()


class EmailBlockNode(template.Node):
    def __init__(self, nodelist, markers):
        self.nodelist = nodelist
        self.markers = markers

    def render(self, context):
        return u'{1}{0}{2}'.format(self.nodelist.render(context), *self.markers)


@register.tag
def dju_email_subject(parser, token):
    nodelist = parser.parse(('enddju_email_subject', 'end_dju_email_subject'))
    parser.delete_first_token()
    return EmailBlockNode(nodelist, DJU_EMAIL_BLOCK_MARKERS['subject'])


@register.tag
def dju_email_plain_body(parser, token):
    nodelist = parser.parse(('enddju_email_plain_body', 'end_dju_email_plain_body'))
    parser.delete_first_token()
    return EmailBlockNode(nodelist, DJU_EMAIL_BLOCK_MARKERS['plain_body'])


@register.tag
def dju_email_html_body(parser, token):
    nodelist = parser.parse(('enddju_email_html_body', 'end_dju_email_html_body'))
    parser.delete_first_token()
    return EmailBlockNode(nodelist, DJU_EMAIL_BLOCK_MARKERS['html_body'])
