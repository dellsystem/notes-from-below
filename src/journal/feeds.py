import datetime

from django.contrib.syndication.views import Feed

from journal.models import Article


class ArticleFeed(Feed):
    title = 'Notes From Below'
    link = 'https://notesfrombelow.org'
    description = 'No politics without inquiry'

    def items(self):
        return Article.objects.filter(published=True).order_by('-date')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.subtitle

    def item_pubdate(self, item):
        return datetime.datetime.combine(item.date, datetime.time())

    def item_author_name(self, item):
        return ', '.join(a.name for a in item.authors.all()) or 'Anonymous'

    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]
