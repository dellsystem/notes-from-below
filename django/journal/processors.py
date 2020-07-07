from .models import Issue, Tag


def header(request):
    return {
        'ISSUES': Issue.objects.filter(published=True),
        'TAGS': Tag.objects.all(),  # todo: get rid of this?
        'LATEST_ISSUE': Issue.objects.filter(published=True).latest(),
    }
