from django.shortcuts import render
from django.views import generic

from .models import Article, Category, Author, Issue, Tag
from blog.models import BlogPost


class ArticleView(generic.DetailView):
    model = Article
    template_name = 'article.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        desired_language_code = self.request.GET.get('language')
        desired_language_name = None  # not needed for English
        article = context['article']
        all_languages = []
        desired_translation = None

        for translation in article.translations.all():
            language_name = translation.get_language_display()
            all_languages.append((translation.language, language_name))
            if translation.language == desired_language_code:
                desired_language_name = language_name
                desired_translation = translation

        # If the get parameter doesn't match an existing translation, use en.
        if desired_translation is None:
            desired_language_code = 'en'
            desired_translation = article

        # Only show "by" (before the author name) for English.
        if desired_language_code == 'en':
            context['by_word'] = 'by '
        else:
            context['by_word'] = ''

        context['formatted'] = desired_translation.formatted_content
        context['unformatted'] = desired_translation.unformatted_content
        context['title'] = desired_translation.title
        context['subtitle'] = desired_translation.subtitle

        # Only add these context variables if translations exist.
        if all_languages:
            all_languages.append(('en', 'English'))

        context['desired_language_code'] = desired_language_code
        context['desired_language_name'] = desired_language_name
        context['languages'] = all_languages
        return context


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
