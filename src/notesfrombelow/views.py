import operator

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from journal.models import Article, Author, Issue, Tag, Category
from cms.models import Page


def index(request):
    issues = Issue.objects.filter(
        published=True,
        number__isnull=False
    ).order_by('-number')[:6]

    context = {
        'issues': issues,
    }

    return render(request, 'index.html', context)


def about(request):
    page = Page.objects.get(slug='about')
    editors = Author.objects.filter(is_editor=True).order_by('name')
    contributors = Author.objects.filter(
        is_editor=False,
        articles__published=True
    ).order_by('name').distinct()

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


def archives(request, page=1, category='all'):
    # If the provided category doesn't match any existing slugs, set to 'all'
    filters = ['all']
    for category_slug in Category.objects.values_list('slug', flat=True):
        filters.append(category_slug)
    if category not in filters:
        category = 'all'

    query = request.GET.get('q', '')
    if len(query) >= 3:
        all_articles = Article.objects.filter(published=True).filter(
            Q(title__icontains=query) | Q(subtitle__icontains=query)
        )
        if category != 'all':
            all_articles = all_articles.filter(category__slug=category)

        # If there are tag or authors containing this query, display them.
        tags = Tag.objects.filter(name__icontains=query)
        authors = Author.objects.filter(name__icontains=query)
    else:
        all_articles = Article.objects.filter(
            published=True
        )
        if category != 'all':
            all_articles = all_articles.filter(category__slug=category)
        tags = Tag.objects.none()
        authors = Author.objects.none()

    paginator = Paginator(all_articles.order_by('-date'), 9)
    articles = paginator.get_page(page)

    context = {
        'articles': articles,
        'page': page,
        'total_pages': paginator.num_pages,
        'total_articles': all_articles.count(),
        'query': query,
        'tags': tags,
        'authors': authors,
        'filters': filters,
        'category': category,
        'categories': Category.objects.all(),
    }

    return render(request, 'archives.html', context)
