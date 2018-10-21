import collections
import math
import operator

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags

from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
from martor.models import MartorField
from martor.utils import markdownify


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField()
    image = ProcessedImageField(
        upload_to='tags',
        processors=[ResizeToFill(1920, 450)],
        options={'quality': 100},
    )
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_articles(self):
        return self.articles.filter(published=True).order_by('-date')

    def get_latest_article(self):
        articles = self.articles.filter(published=True)
        if articles.exists():
            return articles.latest()

    def get_date(self):
        latest = self.get_latest_article()
        if latest:
            return latest.date

    def get_absolute_url(self):
        return reverse('tag', args=[self.slug])


class Category(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20)
    description = models.TextField()
    content = MartorField()
    formatted_content = models.TextField(editable=False)

    class Meta:
        verbose_name_plural = 'categories'

    def get_articles(self):
        return self.articles.filter(published=True).order_by('-date')

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

    def get_articles(self):
        return self.articles.filter(published=True).order_by('-date')

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
    image = ProcessedImageField(
        upload_to='issues',
        processors=[ResizeToFill(1920, 450)],
        options={'quality': 100},
        blank=True
    )
    small_image = ProcessedImageField(
        upload_to='issues',
        processors=[ResizeToFill(540, 360)],
        options={'quality': 100},
    )
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    published = models.BooleanField(default=True)

    class Meta:
        get_latest_by = 'number'

    def save(self, *args, **kwargs):
        self.formatted_content = markdownify(self.content)
        super().save(*args, **kwargs)

    def get_articles(self):
        # If this issue isn't published, just return all the articles.
        if self.published:
            return self.articles.filter(published=True)
        else:
            return self.articles.all()

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
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    subtitle = models.TextField()
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    # Store the formatted_content field with all tags removed (for related)
    unformatted_content = models.TextField(editable=False)
    date = models.DateField()
    issue = models.ForeignKey(Issue, related_name='articles', null=True,
        blank=True, on_delete=models.CASCADE)
    order_in_issue = models.PositiveIntegerField(default=0)
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
    background_position = models.CharField(max_length=50, blank=True)
    image_credit = models.URLField(blank=True)
    related_1 = models.ForeignKey("self", related_name='related_1_articles',
        on_delete=models.CASCADE, blank=True, null=True)
    related_2 = models.ForeignKey("self", related_name='related_2_articles',
        on_delete=models.CASCADE, blank=True, null=True)
    last_modified = models.DateField(auto_now=True)
    published = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['order_in_issue']
        get_latest_by = 'date'

    def __str__(self):
        return self.title

    @property
    def language(self):
        return 'en'

    def get_language_display(self):
        return 'English'

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])

    def get_word_count(self):
        return len(self.unformatted_content.split())

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_content = markdownify(self.content)
        self.unformatted_content = strip_tags(self.formatted_content)
        words = self.unformatted_content.split()

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

            if len(articles) > 1:
                self.related_1 = articles[0][1]
            if len(articles) > 1:
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
        related = []
        if self.related_1:
            related.append(self.related_1)
        if self.related_2:
            related.append(self.related_2)
        return related


class ArticleTranslation(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
        related_name='translations')
    language = models.CharField(max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    # Store the formatted_content field with all tags removed (for description)
    unformatted_content = models.TextField(editable=False)
    # The slug should really have uniqueness checks but, too hard tbh
    slug = models.SlugField(max_length=50)
    last_modified = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('article', 'language')

    def __str__(self):
        return "{}—{}".format(self.article.title, self.get_language_display())

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_content = markdownify(self.content)
        self.unformatted_content = strip_tags(self.formatted_content)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])
