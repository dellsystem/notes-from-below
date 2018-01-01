from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags

from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
from martor.models import MartorField
from martor.utils import markdownify


class Category(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20)
    description = models.TextField()
    image = models.ImageField(upload_to='categories', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('category', args=[self.slug])

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = MartorField()
    formatted_bio = models.TextField(editable=False)
    slug = models.SlugField()
    image = models.ImageField(upload_to='authors')
    is_editor = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('author', args=[self.slug])

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_bio = markdownify(self.bio)
        super().save(*args, **kwargs)


class Issue(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    title =  models.CharField(max_length=50)
    date = models.DateField(help_text='Day ignored')

    class Meta:
        get_latest_by = 'number'

    def __str__(self):
        return self.title


class Article(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
        related_name='articles')
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    authors = models.ManyToManyField(Author, related_name='articles')
    subtitle = models.TextField()
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    date = models.DateField()
    read_time = models.PositiveSmallIntegerField(editable=False)
    issue = models.ForeignKey(Issue, related_name='articles', null=True,
        blank=True, on_delete=models.CASCADE)
    order_in_issue = models.PositiveIntegerField(default=0, editable=False)
    image = ProcessedImageField(
        upload_to='articles',
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

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_content = markdownify(self.content)

        # Calculate the read time.
        num_words = len(strip_tags(self.formatted_content).split())
        self.read_time = max(num_words / 200, 1)  # assuming 200wpm reading speed
        super().save(*args, **kwargs)

    # Use h2 or h3 in article thumbnail depending on the length of the title.
    def get_title_header(self):
        if len(self.title) > 50:
            return 'h3'
        else:
            return 'h2'

    def get_related(self):
        # Limited to 2. Currently just gets the latest articles.
        return Article.objects.order_by('-date')[:2]
