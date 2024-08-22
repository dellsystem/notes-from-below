from django.contrib.sitemaps import Sitemap

from cms.models import Page


class PageSitemap(Sitemap):
    def priority(self, item):
        if item.is_static:
            return 0.4
        else:
            return 0.9

    def changefreq(self, item):
        if item.is_static:
            return 'never'
        else:
            return 'monthly'

    def items(self):
        return Page.objects.filter(published=True).order_by('pk')

    def lastmod(self, item):
        return item.last_modified
