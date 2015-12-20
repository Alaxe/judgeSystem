from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from markdown_deux import markdown

class BlogPost(models.Model):
    title = models.CharField('Title', max_length = 64, default = 'New Draft')

    HTML = 'html'
    MD = 'md'
    CONTENT_LANGUAGE_CHOICES = (
        (HTML, 'HTML'),
        (MD, 'Markdown'),
    )
    content_language = models.CharField('Language', max_length = 8,
        choices = CONTENT_LANGUAGE_CHOICES, default = HTML)

    content = models.TextField('Content', blank = True, default = '')
    author = models.ForeignKey(User)

    public = models.BooleanField(default = False)
    post_time = models.DateTimeField(default = timezone.now)

    class Meta:
        ordering = ('-post_time',)
        permissions = (
            ('change_foreign_blogpost', 'Edit someone else\'s post'),
            ('add_media_to_blogpost', 'Upload media to a blog post'),
        )

    def get_content_html(self):
        if self.content_language == self.HTML:
            return self.content
        elif self.content_language == self.MD:
            return markdown(self.content)

    def may_edit(self, user):
        if not user.is_authenticated():
            return False
        elif user.has_perm('blog.change_foreign_blogpost'):
            return True
        elif self.author == user:
            return True
        else:
            return False
