"""notesfrombelow URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from notesfrombelow.admin import editor_site

import journal.views
import notesfrombelow.views
import cms.views
import blog.views
from journal.feeds import ArticleFeed
from journal.sitemaps import *
from cms.sitemaps import *
from blog.sitemaps import BlogSitemap


sitemaps = {
    'articles': ArticleSitemap(),
    'article_translations': ArticleTranslationSitemap(),
    'authors': AuthorSitemap(),
    'blog': BlogSitemap(),
    'tags': TagSitemap(),
    'categories': CategorySitemap(),
    'issues': IssueSitemap(),
    'pages': PageSitemap(),
}


urlpatterns = [
    path('', notesfrombelow.views.index, name='index'),
    path('about', notesfrombelow.views.about, name='about'),
    path('contribute', notesfrombelow.views.contribute, name='contribute'),
    path('archives/<int:page>', notesfrombelow.views.archives, name='archives'),
    path('archives', notesfrombelow.views.archives, {'page': 1}, name='archives_main'),
    path('blog', notesfrombelow.views.view_blog, name='blog'),
    path('blog/<slug:slug>', blog.views.BlogPostView.as_view(), name='blog-post'),
    path('martor/', include('martor.urls')),
    path('sudo/', admin.site.urls),
    path('editor/', editor_site.urls),
    path('author/<slug:slug>', journal.views.AuthorView.as_view(), name='author'),
    path('category/<slug:slug>', journal.views.CategoryView.as_view(), name='category'),
    path('article/<slug:slug>', journal.views.view_article, name='article'),
    path('issue/<slug:slug>', journal.views.IssueView.as_view(), name='issue'),
    path('issue/<slug:slug>/pdf', journal.views.IssuePdfView.as_view(), name='issue_pdf'),
    path('tag/<slug:slug>', journal.views.TagView.as_view(), name='tag'),
    path('rss/', ArticleFeed()),
    path('<slug:slug>', cms.views.PageView.as_view(), name='page'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
