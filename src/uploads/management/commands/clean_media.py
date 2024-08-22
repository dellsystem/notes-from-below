import os

from django.conf import settings
from django.core.management.base import BaseCommand

from uploads.models import ImageUpload, PdfUpload
from journal.models import Article, Category, Issue
from cms.models import Page


class Command(BaseCommand):
    help = "Removes unused media files from the MEDIA_ROOT dir"

    def handle(self, *args, **options):
        # First get the file paths mentioned in the DB
        file_paths = set()
        models = [
            (ImageUpload, 'file'),
            (PdfUpload, 'file'),
            (Article, 'image'),
            (Page, 'image'),
            (Issue, 'image'),
        ]
        for model, field in models:
            file_paths |= set(model.objects.values_list(field, flat=True))

        # Now get the filepaths on the filesystem
        media_root = settings.MEDIA_ROOT
        for relative_root, dirs, files in os.walk(media_root):
            if relative_root == 'CACHE':
                continue

            for f in files:
                relative_path = os.path.join(os.path.relpath(relative_root, media_root), f)
                if relative_path.startswith('CACHE/'):
                    continue

                if relative_path not in file_paths:
                    print(relative_path)
                    os.remove(os.path.join(media_root, relative_path))
