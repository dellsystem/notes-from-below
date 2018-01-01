from django.contrib import admin

from notesfrombelow.admin import editor_site
from .models import Page


class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']


admin.site.register(Page, PageAdmin)
editor_site.register(Page, PageAdmin)
