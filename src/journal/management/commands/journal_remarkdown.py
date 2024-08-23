from django.core.management.base import BaseCommand

from journal.models import *


class Command(BaseCommand):
    help = 'Refreshes formatted_* fields'

    def handle(self, *args, **options):
        for category in Category.objects.all():
            category.save()
        for author in Author.objects.all():
            author.save()
        for article in Article.objects.all():
            article.save()
        for translation in ArticleTranslation.objects.all():
            translation.save()
