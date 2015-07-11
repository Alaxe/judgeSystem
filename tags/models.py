from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

class Tag(models.Model):
    label = models.CharField('Tag', max_length = 32, unique = True)
    category = models.CharField('Category', max_length = 32)

    class Meta:
        ordering = ('category', 'label')

class TagInstance(models.Model):
    tag = models.ForeignKey(Tag)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = GenericForeignKey('content_type', 'object_id')
