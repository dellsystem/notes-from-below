from django.core.management.base import BaseCommand

from journal.models import *


class Command(BaseCommand):
    help = 'Finds every article with the first tag slug, removes that tag, and adds the second tag'

    def add_arguments(self, parser):
        parser.add_argument('remove_tag', help='slug of the tag to remove')
        parser.add_argument('add_tag', help='slug of the tag to add')

    def handle(self, *args, **options):
        remove_tag = Tag.objects.get(slug=options['remove_tag'])
        add_tag = Tag.objects.get(slug=options['add_tag'])
        print("Removing tag '{}'; adding tag '{}'".format(
            remove_tag.name,
            add_tag.name,
        ))
        for article in remove_tag.articles.all():
            article.tags.add(add_tag)
            article.tags.remove(remove_tag)
