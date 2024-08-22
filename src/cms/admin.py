from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from notesfrombelow.admin import editor_site
from .models import Page


class PageAdmin(CompareVersionAdmin):
    list_display = ['title', 'slug', 'published']


admin.site.register(Page, PageAdmin)
editor_site.register(Page, PageAdmin)
