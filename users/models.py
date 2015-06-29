import string, random

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

def gen_randcode():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(32))

class Confirmation(models.Model):
    code = models.CharField(max_length = 32, default = gen_randcode())
    user = models.OneToOneField(User)
    created = models.DateTimeField(default = timezone.now())

class PassReset(models.Model):
    code = models.CharField(max_length = 32, default = gen_randcode())
    user = models.OneToOneField(User)
    created = models.DateTimeField(default = timezone.now())

class UserStatts(models.Model):
    user = models.OneToOneField(User)

    solvedProblems = models.IntegerField(default = 0)
    triedProblems = models.IntegerField(default = 0)
