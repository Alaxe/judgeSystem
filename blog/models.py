from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class BlogPost(models.Model):
    title = models.CharField('Title', max_length = 64)
    content = models.TextField('Content')
    author = models.ForeignKey(User)

    post_time = models.DateTimeField(default = timezone.now)

    class Meta:
        ordering = ('-post_time',)
        permissions = (
            ('edit_foreign_post', 'Edit someone else\'s post'),
        )
