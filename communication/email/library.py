import datetime
from django.utils.translation import ugettext as _

from django.conf import settings

class Email(object):
    def __init__(self, subject, html_message):
        self.subject = subject
        self.html_message = html_message

class Library(object):
    def __init__(self):
        from .postman import postman

        self.postman = postman

        self.email_prefix = "email/{prefix}_message.html"
        self.subject_prefix = "email/{prefix}_subject.html"

    def get_email(self, template_prefix, context=None, **kwargs):
        if not context:
            context = kwargs

        template_subject = self.subject_prefix.format(prefix=template_prefix)
        template_email = self.email_prefix.format(prefix=template_prefix)

        return self.postman.forge(template_email=template_email,
                                  template_subject=template_subject,
                                  context=context)

library = Library()
