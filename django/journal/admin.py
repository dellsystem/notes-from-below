from django import forms
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import mark_safe

from reversion_compare.admin import CompareVersionAdmin

from notesfrombelow.admin import editor_site
from . import models


class TagAdmin(CompareVersionAdmin):
    list_display = ['name', 'show_image', 'slug', 'category']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def show_image(self, obj):
        if obj.image:
            to_return = '<img src="{}" class="ui medium image" />'.format(
                obj.image.url,
            )
            return mark_safe(to_return)
        else:
            return ''
    show_image.short_description = 'Image'


class IssueAdmin(CompareVersionAdmin):
    list_display = ['number', 'title', 'date', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']


class CategoryAdmin(CompareVersionAdmin):
    list_display = ['name', 'slug', 'tag_name', 'order_on_homepage']
    prepopulated_fields = {'slug': ('name',)}


class AuthorAdmin(CompareVersionAdmin):
    list_display = ['name', 'bio', 'slug', 'twitter']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    search_fields = ['name']


class ArticleForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = '__all__'
        widgets = {
            'image_credit': forms.TextInput(),
            'subtitle': forms.Textarea({'rows': 2}),
        }


def publish(modeladmin, request, queryset):
    queryset.update(published=True)
    messages.info(request, "Published {} article(s)".format(
        queryset.count())
    )


def remove_tags(modeladmin, request, queryset):
    for article in queryset:
        article.tags.remove()

    messages.info(request, "Removed tags from {} article(s)".format(
        queryset.count())
    )


def make_add_tag_action(tag):
    def add_tag(modeladmin, request, queryset):
        for article in queryset:
            article.tags.add(tag)
        messages.info(request, "Added tag '{}' to {} article(s)".format(
            tag.name,
            queryset.count())
        )

    add_tag.short_description = "Add tag '{}'".format(tag.name)
    add_tag.__name__ = 'add_tag_{0}'.format(tag.pk)

    return add_tag


class ArticleAdmin(CompareVersionAdmin):
    list_display = ['display_title', 'date', 'show_image', 'display_tags', 'published', 'is_featured']
    list_filter = ['category', 'tags', 'issue']
    prepopulated_fields = {'slug': ('title',)}
    change_form_template = 'admin/edit_article.html'
    form = ArticleForm
    list_display_links = None
    search_fields = ['title']
    autocomplete_fields = ['related_1', 'related_2', 'issue', 'tags', 'authors']

    def display_title(self, obj):
        if obj.authors.count():
            authors = ', '.join(a.name for a in obj.authors.all())
        else:
            authors = 'anonymous'

        to_return = (
            '<h3 class="ui header"><a href="{edit}">{title}</a><div class="sub header">{subtitle}</div></h3><span>by {authors}</span><br><code><a href="{view}">{slug}</a></code>'.format(
                edit=reverse('editor:journal_article_change', args=[obj.id]),
                title=obj.title,
                subtitle=obj.subtitle or '<em>No subtitle</em>',
                authors=authors,
                view=obj.get_absolute_url(),
                slug=obj.slug,
            )
        )
        return mark_safe(to_return)
    display_title.short_description = 'Article details'

    def display_tags(self, obj):
        html = []

        if obj.issue:
            html.append(
                '<a href="{u}">Issue {n}: {i} (#{o})</a>'.format(
                    u=reverse('editor:journal_issue_change', args=[obj.issue.id]),
                    n=obj.issue.number,
                    i=obj.issue.title,
                    o=obj.order_in_issue
                )
            )

        if obj.category:
            html.append(
                '<a href="{u}"><strong>{c}</strong></a>'.format(
                    u=reverse('editor:journal_category_change', args=[obj.category.id]),
                    c=obj.category
                )
            )

        for tag in obj.tags.all():
            html.append(
                '<div class="ui {c} label">{t}</div>'.format(
                    # highlight tags of the same category as the article
                    c='red' if tag.category and tag.category.pk == obj.category.pk else '',
                    t=tag.name
                )
            )

        return mark_safe('<br />'.join(html))
    display_tags.short_description = 'Issue, category, and tags'

    def show_image(self, obj):
        to_return = '<img src="{}" class="ui medium image" />'.format(
            obj.image.url,
        )
        return mark_safe(to_return)
    show_image.short_description = 'Image'

    def is_featured(self, obj):
        return obj.featured is not None
    is_featured.short_description = 'Featured?'
    is_featured.boolean = True

    def get_actions(self, request):
        actions = super(ArticleAdmin, self).get_actions(request)
        # Make an action to clear all tags
        actions['publish'] = (publish, 'publish', 'Publish')
        actions['remove_tags'] = (remove_tags, 'remove_tags', 'Remove all tags')

        # Make an action for adding each tag
        for tag in models.Tag.objects.all():
            action = make_add_tag_action(tag)
            actions[action.__name__] = (action,
                                        action.__name__,
                                        action.short_description)

        return actions


class FeaturedArticleAdmin(CompareVersionAdmin):
    list_display = ['article', 'order_on_homepage', 'is_thumb']


class ArticleTranslationAdmin(CompareVersionAdmin):
    list_display = ['article', 'title', 'slug', 'language']
    prepopulated_fields = {'slug': ('title',)}


editor_site.register(models.Issue, IssueAdmin)
editor_site.register(models.Article, ArticleAdmin)
editor_site.register(models.ArticleTranslation, ArticleTranslationAdmin)
editor_site.register(models.FeaturedArticle, FeaturedArticleAdmin)
editor_site.register(models.Author, AuthorAdmin)
editor_site.register(models.Category, CategoryAdmin)
editor_site.register(models.Tag, TagAdmin)

admin.site.register(models.Issue, IssueAdmin)
admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.ArticleTranslation, ArticleTranslationAdmin)
admin.site.register(models.FeaturedArticle, FeaturedArticleAdmin)
admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Tag, TagAdmin)
