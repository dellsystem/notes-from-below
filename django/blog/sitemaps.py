from django.contrib.sitemaps import Sitemap

from blog.models import BlogPost


class BlogSitemap(Sitemap):
    def priority(self, item):
        return 0.3

    def changefreq(self, item):
        return 'never'

    def items(self):
        return BlogPost.objects.filter(published=True).order_by('pk')

    def lastmod(self, item):
        return item.last_modified
