from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from notesfrombelow.admin import editor_site
from .models import BlogPost


class BlogPostAdmin(CompareVersionAdmin):
    list_display = ['title', 'slug', 'published']
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(BlogPost, BlogPostAdmin)
editor_site.register(BlogPost, BlogPostAdmin)
