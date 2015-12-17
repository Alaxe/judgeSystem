import string, random

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.utils import timezone

def gen_randcode():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.SystemRandom().choice(chars) for i in range(32))

class UserLink(models.Model):
    code = models.CharField(max_length = 32, default = gen_randcode)
    user = models.OneToOneField(User)
    created = models.DateTimeField(default = timezone.now)

    def gen_new_code(self):
        self.code = gen_randcode()
        self.save()

    class Meta:
        abstract = True

class Confirmation(UserLink):
    def __str__(self):
        return self.user.username + ' confirmation ' + self.code

class PassReset(UserLink):
    def __str__(self):
        return self.user.username + ' password reset ' + self.code
