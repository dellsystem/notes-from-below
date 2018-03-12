from django.db import models

from imagekit.processors import ResizeToFit
from imagekit.models import ProcessedImageField


class ImageUpload(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    file = ProcessedImageField(
        upload_to='images',
        processors=[ResizeToFit(width=1115, upscale=False)],
    )


class PdfUpload(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    file = models.FileField(upload_to='pdfs')
    png_file = models.ImageField(upload_to='pdf_pngs', blank=True, null=True)

    def __str__(self):
        return self.title
