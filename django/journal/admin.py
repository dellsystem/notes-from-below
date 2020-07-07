from django import forms
from django.contrib import admin, messages

from reversion_compare.admin import CompareVersionAdmin

from notesfrombelow.admin import editor_site
from . import models


class TagAdmin(CompareVersionAdmin):
    list_display = ['name', 'slug', 'category']
    prepopulated_fields = {'slug': ('name',)}


class IssueAdmin(CompareVersionAdmin):
    list_display = ['number', 'title', 'date', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class CategoryAdmin(CompareVersionAdmin):
    list_display = ['name', 'slug', 'tag_name', 'order_on_homepage']
    prepopulated_fields = {'slug': ('name',)}


class AuthorAdmin(CompareVersionAdmin):
    list_display = ['name', 'bio', 'slug', 'twitter']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


class ArticleForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = '__all__'
        widgets = {
            'image_credit': forms.TextInput(),
            'tags': forms.SelectMultiple(
                attrs={
                    'class': 'ui search fluid dropdown multi-select',
                },
            ),
            'authors': forms.SelectMultiple(
                attrs={
                    'class': 'ui search fluid dropdown multi-select',
                },
            ),
            'subtitle': forms.TextInput(),
            'related_2': forms.Select(
                attrs={
                    'class': 'ui search fluid dropdown',
                },
            ),
            'related_1': forms.Select(
                attrs={
                    'class': 'ui search fluid dropdown',
                },
            ),
        }


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
    list_display = ['title', 'list_authors', 'category', 'issue', 'list_tags',
        'order_in_issue', 'date', 'published', 'featured']
    readonly_fields = ['image_thumbnail']
    list_filter = ['tags', 'issue']
    prepopulated_fields = {'slug': ('title',)}
    change_form_template = 'admin/edit_article.html'
    form = ArticleForm
    search_fields = ['title']

    def list_tags(self, obj):
        return ', '.join(a.name for a in obj.tags.all())

    def list_authors(self, obj):
        return ', '.join(a.name for a in obj.authors.all())

    def get_actions(self, request):
        actions = super(ArticleAdmin, self).get_actions(request)

        for tag in models.Tag.objects.all():
            action = make_add_tag_action(tag)
            actions[action.__name__] = (action,
                                        action.__name__,
                                        action.short_description)

        return actions


class ArticleTranslationAdmin(CompareVersionAdmin):
    list_display = ['article', 'title', 'slug', 'language']
    prepopulated_fields = {'slug': ('title',)}


editor_site.register(models.Issue, IssueAdmin)
editor_site.register(models.Article, ArticleAdmin)
editor_site.register(models.ArticleTranslation, ArticleTranslationAdmin)
editor_site.register(models.Author, AuthorAdmin)
editor_site.register(models.Category, CategoryAdmin)
editor_site.register(models.Tag, TagAdmin)

admin.site.register(models.Issue, IssueAdmin)
admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.ArticleTranslation, ArticleTranslationAdmin)
admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Tag, TagAdmin)
