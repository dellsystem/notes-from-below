from django.http import Http404
from django.shortcuts import render
from django.views import generic

from .models import Article, ArticleTranslation, Category, Author, Issue, Tag
from blog.models import BlogPost


class ArticleView(generic.DetailView):
    model = Article
    template_name = 'article.html'

def view_article(request, slug):
    # If there's an article with slug, go with that. If not, check translations
    article = Article.objects.filter(slug=slug).first()
    if article:
        # For backwards compatibility, check if a language is specified.
        desired_translation = None
        desired_language_code = request.GET.get('language')
    else:
        desired_translation = ArticleTranslation.objects.filter(slug=slug).first()
        if desired_translation:
            desired_language_code = desired_translation.language
            article = desired_translation.article
        else:
            raise Http404

    all_languages = []
    desired_language_name = None  # not needed for English

    for translation in article.translations.all():
        language_name = translation.get_language_display()
        all_languages.append(
            (
                translation.language,
                language_name,
                translation.get_absolute_url()
            )
        )
        if translation.language == desired_language_code:
            desired_language_name = language_name
            desired_translation = translation

    # If the get parameter doesn't match an existing translation, use en.
    if desired_translation is None:
        desired_language_code = 'en'
        desired_translation = article

    # Only show "by" (before the author name) for English.
    if desired_language_code == 'en':
        by_word = 'by '
    else:
        by_word = ''

    # Only add these context variables if translations exist.
    if all_languages:
        all_languages.append(('en', 'English', article.get_absolute_url()))

    context = {
        'formatted': desired_translation.formatted_content,
        'unformatted': desired_translation.unformatted_content,
        'title': desired_translation.title,
        'subtitle': desired_translation.subtitle,
        'desired_language_code': desired_language_code,
        'desired_language_name': desired_language_name,
        'languages': all_languages,
        'article': article,
    }
    return render(request, 'article.html', context)


class CategoryView(generic.DetailView):
    model = Category
    template_name = 'category.html'


class AuthorView(generic.DetailView):
    model = Author
    template_name = 'author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['author'].slug == 'ed-emery':
            context['posts'] = BlogPost.objects.filter(published=True)
        return context

class IssueView(generic.DetailView):
    model = Issue
    template_name = 'issue.html'


class IssuePdfView(generic.DetailView):
    model = Issue
    template_name = 'issue_pdf.html'


class TagView(generic.DetailView):
    model = Tag
    template_name = 'tag.html'
