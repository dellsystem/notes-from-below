from django.db import models
from django.urls import reverse

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from martor.models import MartorField
from martor.utils import markdownify


class Page(models.Model):
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
    image = ProcessedImageField(
        upload_to='pages',
        processors=[ResizeToFit(width=500, upscale=False)],
        format='JPEG',
        options={'quality': 100},
        help_text="Resized to 540x360.",
        blank=True,
        null=True
    )

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
