from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags

from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
from martor.models import MartorField
from martor.utils import markdownify

from journal.utils import find_similar_articles


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
    icon = models.CharField(
        max_length=10,
        help_text="Semantic UI icon used for the label on the article page"
    )
    archive_link_text = models.CharField(
        max_length=20,
        help_text="The text shown on the homepage for linking to this archive"
    )

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['order_on_homepage']

    def get_latest_articles(self):
        return self.get_articles()[:9]

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
    # TODO: validation on number & is_book (number needed if is_book is False)
    number = models.PositiveSmallIntegerField(unique=True, blank=True,
        null=True,
        help_text="Set this for regular issues. Leave it blank for books.")
    is_book = models.BooleanField(default=False)
    title =  models.CharField(max_length=50)
    date = models.DateField(help_text='Day ignored')
    slug = models.SlugField()
    image = ProcessedImageField(
        upload_to='issues',
        options={'quality': 100},
        processors=[ResizeToFill(width=500, upscale=False)],
        help_text="Cropped to 500 pixels wide (no height specified)"
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
    # Handle basic Markdown formatting in the subtitle (eg italics)
    formatted_subtitle = models.TextField(editable=False)
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
    def get_language_code(self):
        return 'en'

    @property
    def get_language_name(self):
        return 'English'

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])

    def get_word_count(self):
        return len(self.unformatted_content.split())

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_subtitle = markdownify(self.subtitle)
        self.formatted_content = markdownify(self.content)
        self.unformatted_content = strip_tags(self.formatted_content)

        # If we're missing a related article, find the two most similar
        # articles based on cosine similarity.
        if not self.related_1 or not self.related_2:
            other_articles = Article.objects.exclude(pk=self.pk)
            related_1, related_2 = find_similar_articles(self.unformatted_content, other_articles)
            if not self.related_1:
                self.related_1 = related_1
            if not self.related_2:
                self.related_2 = related_2

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


class TranslationLanguage(models.Model):
    code = models.CharField(
        max_length=2,
        primary_key=True,
        help_text='A two-letter code for the language from ISO 639. e.g., en, fr.'
    )
    name = models.CharField(
        max_length=50,
        help_text='The name of the language as it appears in that language.'
    )

    def __str__(self):
        return self.name


class ArticleTranslation(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='translations'
    )
    translation_language = models.ForeignKey(
        TranslationLanguage,
        on_delete=models.PROTECT
    )
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    formatted_subtitle = models.TextField(editable=False)
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    # Store the formatted_content field with all tags removed (for description)
    unformatted_content = models.TextField(editable=False)
    # The slug should really have uniqueness checks but, too hard tbh
    slug = models.SlugField(max_length=50)
    last_modified = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('article', 'translation_language')

    def __str__(self):
        return "{}—{}".format(self.article.title, self.translation_language.name)

    # The two below are useful for the template (for English)
    def get_language_code(self):
        return self.translation_language.code

    def get_language_name(self):
        return self.translation_language.name

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_subtitle = markdownify(self.subtitle)
        self.formatted_content = markdownify(self.content)
        self.unformatted_content = strip_tags(self.formatted_content)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])
