import os

from django.core.management.base import BaseCommand
from django.conf import settings

from journal.models import *


class Command(BaseCommand):
    help = 'cleans up media dir'

    def handle(self, *args, **options):
        # make sure that all article image files use the article slug
        names = set()
        for article in Article.objects.all():
            original_path = article.image.path
            original_name = article.image.name
            new_name = '{}.jpg'.format(article.slug)
            full_name = 'articles/{}'.format(new_name)
            names.add(new_name)
            if full_name == original_name:
                continue

            article.image.name = full_name
            new_path = os.path.join(os.path.dirname(article.image.path), new_name)
            print('renaming', original_name, full_name)
            print('----')
            os.rename(original_path, new_path)
            article.save()

        # go through the directory and delete unused images
        for filename in os.listdir('media/articles'):
            if filename not in names:
                print('removing', filename)
                os.remove(os.path.join('media/articles', filename))
