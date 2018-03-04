from django.db import models
from django.urls import reverse

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from martor.models import MartorField
from martor.utils import markdownify


class Page(models.Model):
    image = ProcessedImageField(
        upload_to='pages',
        processors=[ResizeToFill(1920, 1080)],
        format='JPEG',
        options={'quality': 100},
        blank=True
    )
    background_position = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=100, blank=True)
    subtitle = models.TextField(blank=True)
    content = MartorField(blank=True)
    formatted_content = models.TextField(editable=False)
    slug = models.SlugField(blank=True, unique=True)
    last_modified = models.DateField(auto_now=True)
    is_static = models.BooleanField(default=True,
        help_text='Ignore this. For sitemap usage only'
    )
    published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.slug:
            return reverse('page', args=[self.slug])
        else:
            return '/'

    def save(self, *args, **kwargs):
        self.formatted_content = markdownify(self.content)
        super().save(*args, **kwargs)
