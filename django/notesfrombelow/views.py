import operator

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from journal.models import Article, Author, Issue, Tag, Category, FeaturedArticle
from cms.models import Page


def index(request):

    latest_issues = Issue.objects.order_by('-date')

    inquiry = Category.objects.get(slug='inquiry')
    theory = Category.objects.get(slug='theory')
    bulletins = Category.objects.get(slug='bulletins')
    featured_articles = FeaturedArticle.objects.all()
    large_features = featured_articles.filter(is_thumb=False)
    small_features = featured_articles.filter(is_thumb=True)

    context = {
        'issues': Issue.objects.filter(published=True).order_by('-number'),
        'categories': Category.objects.all(),
        'large_features': large_features,
        'small_features': small_features,
        'themes': theory.tags.all(),
        'bulletin_publications': bulletins.tags.all(),
        'inquiry_sectors': inquiry.tags.all(),
        'latest_issue': latest_issues[0],
        'previous_issue': latest_issues[1],
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

    paginator = Paginator(all_articles.order_by('-date'), 10)
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
    }

    return render(request, 'archives.html', context)
