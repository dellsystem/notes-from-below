from django import forms
from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from notesfrombelow.admin import editor_site
from . import models


class IssueAdmin(CompareVersionAdmin):
    list_display = ['number', 'title', 'date', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class CategoryAdmin(CompareVersionAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class AuthorAdmin(CompareVersionAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ArticleForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = '__all__'
        widgets = {
            'image_credit': forms.TextInput(),
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


class ArticleAdmin(CompareVersionAdmin):
    list_display = ['title', 'list_authors', 'category', 'issue',
        'order_in_issue', 'date', 'published', 'featured']
    readonly_fields = ['image_thumbnail']
    list_filter = ['issue']
    prepopulated_fields = {'slug': ('title',)}
    change_form_template = 'admin/edit_article.html'
    form = ArticleForm

    def list_authors(self, obj):
        return ', '.join(a.name for a in obj.authors.all())


class ArticleTranslationAdmin(CompareVersionAdmin):
    list_display = ['article', 'title', 'language']


editor_site.register(models.Issue, IssueAdmin)
editor_site.register(models.Article, ArticleAdmin)
editor_site.register(models.ArticleTranslation, ArticleTranslationAdmin)
editor_site.register(models.Author, AuthorAdmin)
editor_site.register(models.Category, CategoryAdmin)

admin.site.register(models.Issue, IssueAdmin)
admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.ArticleTranslation, ArticleTranslationAdmin)
admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.Category, CategoryAdmin)
