from .models import Issue, Tag


def header(request):
    return {
        'ISSUES': Issue.objects.filter(published=True),
        'TAGS': Tag.objects.filter(featured=True),
        'LATEST_ISSUE': Issue.objects.filter(published=True).latest(),
    }
