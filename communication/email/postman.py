import requests
from django.conf import settings

from django.template.loader import get_template
from django.template import Context

class Postman(object):
    def __init__(self, api_key="yoooooo", domain_name="yooooo", poster=None):
        self.api_key = api_key
        self.domain_name = domain_name

        if not poster:
            self.poster = "erer" + "@" + domain_name

        super(Postman, self).__init__()

    def forge(self, template_email, template_subject, context=None):
        if not context:
            context = {}

        subject_template = get_template(template_subject)
        email_template = get_template(template_email)

        subject = subject_template.template.render(Context(context)).strip()
        html_message = email_template.template.render(Context(context)).strip()

        from .library import Email
        return Email(subject, html_message)

    def send_email(self, subject, html_message, recipient_list):
        try:
            pass 
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print("E-mail not sent. Requests Error: %s" % str(e))

postman = Postman()
