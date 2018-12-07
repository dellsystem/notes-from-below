import operator

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from journal.models import Article, Author, Issue, Tag
from cms.models import Page
from blog.models import BlogPost


def index(request):
    page = Page.objects.get(slug='')

    tags = []
    for tag in Tag.objects.filter(featured=True):
        article = tag.get_latest_article()
        if article:
            tags.append((tag, article, article.date))
    tags.sort(key=operator.itemgetter(2), reverse=True)

    context = {
        'tags': tags,
        'issues': Issue.objects.filter(published=True).order_by('-number'),
        'page': page,
        'posts': BlogPost.objects.filter(published=True).order_by('-date')[:2],
        'blog_author': Author.objects.get(slug='ed-emery'),
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


def archives(request, page=1):
    query = request.GET.get('q', '')
    if len(query) >= 3:
        all_articles = Article.objects.filter(published=True).filter(
            Q(title__icontains=query) | Q(subtitle__icontains=query)
        ).order_by('-date')

        # If there are tag or authors containing this query, display them.
        tags = Tag.objects.filter(name__icontains=query)
        authors = Author.objects.filter(name__icontains=query)
    else:
        all_articles = Article.objects.filter(published=True).order_by('-date')
        tags = Tag.objects.none()
        authors = Author.objects.none()

    paginator = Paginator(all_articles, 10)
    articles = paginator.get_page(page)

    context = {
        'articles': articles,
        'page': page,
        'total_pages': paginator.num_pages,
        'total_articles': all_articles.count(),
        'query': query,
        'tags': tags,
        'authors': authors,
    }

    return render(request, 'archives.html', context)


def view_blog(request):
    posts = BlogPost.objects.filter(published=True).order_by('-date')
    page = Page.objects.get(slug='blog')
    context = {
        'posts': posts,
        'page': page,
        'author': Author.objects.get(slug='ed-emery'),
    }

    return render(request, 'blog.html', context)
