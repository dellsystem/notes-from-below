from django.db import models

from django.urls import reverse
from django.utils.html import strip_tags

from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
from martor.models import MartorField
from martor.utils import markdownify


class BlogPost(models.Model):
    """Assume that all articles are authored by Ed Emery."""
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    slug = models.SlugField()
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    preview = models.TextField(editable=False)
    date = models.DateField()
    image = ProcessedImageField(
        upload_to='blog',
        processors=[ResizeToFill(1920, 1080)],
        format='JPEG',
        options={'quality': 100}
    )
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(540, 360)],
        format='JPEG',
        options={'quality': 90}
    )
    background_position = models.CharField(max_length=50, blank=True)
    image_credit = models.URLField(blank=True)
    published = models.BooleanField(default=True)
    last_modified = models.DateField(auto_now=True)

    class Meta:
        get_latest_by = 'date'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog-post', args=[self.slug])

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_content = markdownify(self.content)
        self.preview = strip_tags(self.formatted_content)[:500]

        super().save(*args, **kwargs)
