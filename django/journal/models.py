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


class Category(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20)
    description = models.TextField()
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    tag_name = models.CharField(
        max_length=12,
        help_text="Singular word for what the tags refer to (e.g., theme)"
    )
    about_page = models.ForeignKey('cms.Page', on_delete=models.PROTECT, blank=True, null=True)
    order_on_homepage = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=10,
        help_text="Semantic UI icon used for the label on the article page")
    archive_link_text = models.CharField(
        max_length=20,
        help_text="The text shown on the homepage for linking to this archive"
    )

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['order_on_homepage']

    def get_latest_article(self):
        return self.articles.filter(published=True).latest()

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


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField()
    image = ProcessedImageField(
        upload_to='tags',
        processors=[ResizeToFill(540, 360)],
        options={'quality': 100},
        blank=True,
        null=True,
        help_text="Resized to 540x360",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='tags', null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_articles(self):
        # only show articles whose category matches the tag category
        return self.articles.filter(
            category=self.category,
            published=True
        ).order_by('-date')

    def get_latest_article(self, existing_articles=None):
        articles = self.articles.filter(published=True)
        if existing_articles:
            articles = articles.exclude(pk__in=existing_articles)

        if articles.exists():
            return articles.latest()

    def get_date(self):
        latest = self.get_latest_article()
        if latest:
            return latest.date

    def get_absolute_url(self):
        return reverse('tag', args=[self.slug])


class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = MartorField()
    formatted_bio = models.TextField(editable=False)
    slug = models.SlugField(unique=True)
    is_editor = models.BooleanField(default=False)
    twitter = models.CharField(max_length=15, blank=True, help_text='Username without the @')

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
        processors=[ResizeToFill(540, 360)],
        options={'quality': 100},
        help_text='Cropped to 540x360'
    )
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    published = models.BooleanField(default=False)

    class Meta:
        get_latest_by = 'date'
        ordering = ['-date']

    def save(self, *args, **kwargs):
        self.formatted_content = markdownify(self.content)
        super().save(*args, **kwargs)

    def get_articles(self):
        # If this issue isn't published, just return all the articles.
        if self.published:
            return self.articles.filter(published=True)
        else:
            return self.articles.all()

    # Use h2 or h3 in footer depending on the length of the title.
    def get_title_header(self):
        if len(self.title) > 30:
            return 'h3'
        else:
            return 'h2'

    def get_absolute_url(self):
        return reverse('issue', args=[self.slug])

    def __str__(self):
        return self.title


class Article(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
        related_name='articles')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
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
        processors=[ResizeToFill(540, 360)],
        format='JPEG',
        options={'quality': 100},
        help_text="Resized to 540x360."
    )
    image_credit = models.URLField(blank=True)
    related_1 = models.ForeignKey("self", related_name='related_1_articles',
        on_delete=models.CASCADE, blank=True, null=True)
    related_2 = models.ForeignKey("self", related_name='related_2_articles',
        on_delete=models.CASCADE, blank=True, null=True)
    last_modified = models.DateField(auto_now=True)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', 'order_in_issue']
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

    # Use h3 or h4 in article thumbnail depending on the length of the title.
    def get_title_header(self):
        if len(self.title) > 50:
            return 'h4'
        else:
            return 'h3'

    def get_related(self):
        # Limited to 2. Currently just gets the latest articles.
        related = []
        if self.related_1:
            related.append(self.related_1)
        if self.related_2:
            related.append(self.related_2)
        return related


class FeaturedArticle(models.Model):
    """For featured articles on the homepage. Can be full width or thumbnail."""
    article = models.OneToOneField(
        Article,
        related_name="featured",
        on_delete=models.CASCADE,
        primary_key=True
    )
    is_thumb = models.BooleanField(
        help_text="Check this if you want the box to be small, rather than taking up the whole container"
    )
    order_on_homepage = models.PositiveIntegerField(
        unique=True,
        help_text="For determining the order of articles on the homepage. 1, 2, 3, etc. Note that large (non-thumb) articles will always be shown first."
    )
    
    def __str__(self):
        return self.article.title

    class Meta:
        ordering = ['order_on_homepage']


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
