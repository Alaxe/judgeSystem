import string, random

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType 
from django.db import models

def get_mediafile_loc(instance, filename):
    chars = string.ascii_uppercase + string.digits
    rand_str = ''.join(random.SystemRandom().choice(chars) for i in range(32))

    return '{0}.{1}'.format(rand_str, 
        filename.split('.')[-1])

class MediaFile(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    media = models.FileField(upload_to = get_mediafile_loc)
    filename = models.CharField(max_length = 32)

    def __str__(self):
        return self.filename

    @staticmethod
    def get_for_object(obj):
        model_type = ContentType.objects.get_for_model(type(obj))
        return MediaFile.objects.filter(content_type = model_type, 
            object_id = obj.id)
