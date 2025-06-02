from django.db import models

from imagekit.processors import ResizeToFit
from imagekit.models import ProcessedImageField
from pdf2image import convert_from_path
from PIL import Image


class ImageUpload(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    file = ProcessedImageField(
        upload_to='images',
        processors=[ResizeToFit(width=1115, upscale=False)],
    )
    alt = models.CharField(max_length=255, blank=True,
        help_text="A description of the image, for accessibility (optional)")

    def __str__(self):
        return "Image: {title}".format(title=self.title)


class PdfUpload(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    file = models.FileField(upload_to='pdfs')

    def __str__(self):
        return "PDF: {title}".format(title=self.title)

    def save(self, *args, **kwargs):
        super(PdfUpload, self).save(*args, **kwargs)
        if getattr(self, '_file_changed', True):
            self.generate_png()

    def generate_png(self):
        images = convert_from_path(self.file.path, dpi=150)
        widths, heights = zip(*(i.size for i in images))
        total_height = sum(heights)
        max_width = max(widths)
        new_image = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for image in images:
            new_image.paste(image, (0, y_offset))
            y_offset += image.size[1]
        new_image.save(self.file.path + '.png')


class OtherUpload(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    file = models.FileField(upload_to='other')
    extension = models.CharField(
        max_length=10,
        help_text='Human-readable file extension (e.g., epub, docx, etc)'
    )
