from django.contrib.sitemaps import Sitemap

from blog.models import BlogPost


class BlogSitemap(Sitemap):
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
        return BlogPost.objects.filter(published=True).order_by('pk')

    def lastmod(self, item):
        return item.last_modified
