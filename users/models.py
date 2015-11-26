import string, random

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.utils import timezone

def gen_randcode():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.SystemRandom().choice(chars) for i in range(32))

class UserLink(models.Model):
    code = models.CharField(max_length = 32, default = '')
    user = models.OneToOneField(User)
    created = models.DateTimeField(default = timezone.now)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(UserLink, self).__init__(*args, **kwargs)
        self.code = gen_randcode()

class Confirmation(UserLink):
    def __str__(self):
        return self.user.username + ' confirm'

class PassReset(UserLink):
    pass
