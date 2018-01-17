from django.core.management.base import BaseCommand

from cms.models import *


class Command(BaseCommand):
    help = 'Refreshes formatted_* fields'

    def handle(self, *args, **options):
        for page in Page.objects.all():
            page.save()
