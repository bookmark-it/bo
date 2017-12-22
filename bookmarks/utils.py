import requests

from django.contrib.auth.models import User

def forwardRequest (data):
    hook_users = User.objects.filter(hook__active=True)

    for hook_user in hook_users:
        try:
            r = requests.post(hook_user.hook.url, data = data)
        except Exception as e:
            raise
