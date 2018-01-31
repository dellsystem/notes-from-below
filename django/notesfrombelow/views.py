from django.shortcuts import render

from journal.models import Article, Author
from cms.models import Page


def index(request):
    articles = Article.objects.order_by('order_in_issue')
    page = Page.objects.get(slug='')

    context = {
        'articles': articles,
        'page': page,
    }

    return render(request, 'index.html', context)


def about(request):
    page = Page.objects.get(slug='about')
    editors = Author.objects.filter(is_editor=True)
    contributors = Author.objects.filter(is_editor=False)

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
