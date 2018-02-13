from django.contrib.sitemaps import Sitemap

from journal.models import Article, Author, Category, Issue


class ArticleSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.7

    def items(self):
        return Article.objects.all()

    def lastmod(self, item):
        return item.last_modified


class AuthorSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.4

    def items(self):
        return Author.objects.order_by('name')

    def lastmod(self, item):
        try:
            return item.articles.latest().date
        except Article.DoesNotExist:
            return None


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Category.objects.order_by('name')

    def lastmod(self, item):
        try:
            return item.articles.latest().date
        except Article.DoesNotExist:
            return None


class IssueSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.9

    def items(self):
        return Issue.objects.order_by('pk')

    def lastmod(self, item):
        return item.date
