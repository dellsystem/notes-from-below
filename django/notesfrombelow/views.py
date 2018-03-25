from django.shortcuts import render

from journal.models import Article, Author, Issue, Tag
from cms.models import Page


def index(request):
    articles = Article.objects.filter(published=True).order_by('order_in_issue')
    page = Page.objects.get(slug='')

    tags = []
    for tag in Tag.objects.filter(featured=True):
        article = tag.get_latest_article()
        if article:
            tags.append((tag, article))

    context = {
        'tags': tags,
        'issues': Issue.objects.order_by('-number'),
        'articles': articles,
        'page': page,
    }

    return render(request, 'index.html', context)


def about(request):
    page = Page.objects.get(slug='about')
    editors = Author.objects.filter(is_editor=True)
    contributors = Author.objects.filter(
        is_editor=False,
        articles__published=True
    )

    context = {
        'page': page,
        'editors': editors,
        'contributors': contributors,
    }

    return render(request, 'about.html', context)


def contribute(request):
    page = Page.objects.get(slug='contribute')

    context = {
        'page': page,
    }

    return render(request, 'contribute.html', context)
