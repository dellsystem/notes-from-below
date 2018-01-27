import collections
import math
import operator

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
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    image = ProcessedImageField(
        upload_to='categories',
        processors=[ResizeToFill(1920, 1080)],
        format='JPEG',
        options={'quality': 100},
    )

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('category', args=[self.slug])

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_content = markdownify(self.content)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = MartorField()
    formatted_bio = models.TextField(editable=False)
    slug = models.SlugField()
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
    slug = models.SlugField()

    class Meta:
        get_latest_by = 'number'

    def get_absolute_url(self):
        return reverse('issue', args=[self.slug])

    def __str__(self):
        return self.title


class Article(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
        related_name='articles')
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    authors = models.ManyToManyField(Author, related_name='articles',
        blank=True)
    subtitle = models.TextField()
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    # Store the formatted_content field with all tags removed (for related)
    unformatted_content = models.TextField(editable=False)
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
    image_credit = models.URLField(blank=True)
    related_1 = models.ForeignKey("self", related_name='related_1_articles',
        on_delete=models.CASCADE, blank=True, null=True)
    related_2 = models.ForeignKey("self", related_name='related_2_articles',
        on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_content = markdownify(self.content)
        self.unformatted_content = strip_tags(self.formatted_content)
        words = self.unformatted_content.split()

        # Calculate the read time.
        self.read_time = max(len(words) / 200, 1)  # assuming 200wpm reading speed

        # Find the two most similar articles based on cosine similarity. Only
        # do this if they're missing!
        if not self.related_1 or not self.related_2:
            this_counter = collections.Counter(words)
            articles = []
            for article in Article.objects.exclude(slug=self.slug):
                other_counter = collections.Counter(article.unformatted_content.split())
                intersection = set(this_counter.keys()) & set(other_counter.keys())
                numerator = sum([this_counter[x] * other_counter[x] for x in intersection])

                this_sum = sum([v**2 for v in this_counter.values()])
                other_sum = sum([v**2 for v in this_counter.values()])
                denominator = math.sqrt(this_sum) * math.sqrt(other_sum)

                cosine = numerator / denominator if denominator else 0.0
                articles.append((cosine, article))
            articles.sort(key=operator.itemgetter(0), reverse=True)

            self.related_1 = articles[0][1]
            self.related_2 = articles[1][1]

        super().save(*args, **kwargs)

    # Use h2 or h3 in article thumbnail depending on the length of the title.
    def get_title_header(self):
        if len(self.title) > 50:
            return 'h3'
        else:
            return 'h2'

    def get_related(self):
        # Limited to 2. Currently just gets the latest articles.
        return [self.related_1, self.related_2]
