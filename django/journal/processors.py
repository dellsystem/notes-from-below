from .models import Issue


def latest_issue(request):
    return {
        'LATEST_ISSUE': Issue.objects.filter(published=True).latest(),
    }
