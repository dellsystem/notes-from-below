import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import generic

from .models import Article, ArticleTranslation, Category, Author, Issue, Tag
from blog.models import BlogPost


class ArticleView(generic.DetailView):
    model = Article
    template_name = 'article.html'


@staff_member_required
def issue_publish(request, slug):
    issue = Issue.objects.filter(slug=slug).first()
    if not issue:
        raise Http404

    if issue.published:
        return redirect(issue)

    today = datetime.date.today()
    if request.method == 'POST':
        # Publish the articles, change all the article dates to today, and make
        # the issue live.
        issue.articles.all().update(published=True, date=today)
        issue.published = True
        issue.save()
        return redirect(issue)

    context = {
        'issue': issue,
    }
    return render(request, 'issue_publish.html', context)


def view_article(request, slug):
    # First check if this slug is for an ArticleTranslation. If not, try a
    # regular article (and redirect away the language code if necessary).
    desired_translation = ArticleTranslation.objects.filter(slug=slug).first()
    if desired_translation:
        article = desired_translation.article
    else:
        article = Article.objects.filter(slug=slug).first()
        language_code = request.GET.get('language')
        if language_code:
            desired_translation = ArticleTranslation.objects.filter(
                language=language_code,
                article=article,
            ).first()
            if desired_translation:
                return redirect(desired_translation)
            else:
                # The article exists, but the translation doesn't. Show 404.
                raise Http404
        else:
            # Assume English.
            desired_translation = article

        if not article:
            raise Http404

    translations = [translation for translation in article.translations.all()]
    if translations:
        # If there are other languages, add the main article (for English).
        translations.append(article)

    context = {
        'translations': translations,
        'article': article,
        'desired_translation': desired_translation,
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
        else:
            context['posts'] = None
        return context

class IssueView(generic.DetailView):
    model = Issue
    template_name = 'issue.html'


class IssueListView(generic.ListView):
    model = Issue
    template_name = 'issues.html'

    def get_queryset(self):
        """For the main issues page we only show non-book issues. This is a
        little annoying logically but we're currently using the Issue model to
        hold both regular issues and books so it'll have to do for now."""
        return Issue.objects.exclude(is_book=True)


class BookListView(generic.ListView):
    model = Issue
    template_name = 'books.html'

    def get_queryset(self):
        return Issue.objects.filter(is_book=True)


class IssuePdfView(generic.DetailView):
    model = Issue
    template_name = 'issue_pdf.html'


class TagView(generic.DetailView):
    model = Tag
    template_name = 'tag.html'
