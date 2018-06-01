from django.views import generic

from .models import BlogPost
from journal.models import Author


class BlogPostView(generic.DetailView):
    model = BlogPost
    template_name = 'blog_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = Author.objects.get(slug='ed-emery')

        post = context['blogpost']
        other_posts = []
        # Get the posts published directly before and after, if they exist.
        before = BlogPost.objects.filter(pk__lt=post.pk).order_by('pk').last()
        if before:
            other_posts.append(before)
        after = BlogPost.objects.filter(pk__gt=post.pk).order_by('pk').first()
        if after:
            other_posts.append(after)
        context['other_posts'] = other_posts

        return context
