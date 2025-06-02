from django.contrib import admin
from django.forms import TextInput
from django.utils.html import mark_safe

from reversion_compare.admin import CompareVersionAdmin

from notesfrombelow.admin import editor_site
from .models import *


class ImageUploadAdmin(CompareVersionAdmin):
    list_display = ['display_title', 'slug', 'alt', 'show_image']
    prepopulated_fields ={'slug': ('title',),}
    search_fields = ['title', 'alt']
    readonly_fields = ['show_image']
    # I just want the alt field to be wider but it's easiest to widen them all
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 100})}
    }

    def display_title(self, obj):
        to_return = '{title} ({width} x {height})'.format(
            title=obj.title,
            width=obj.file.width,
            height=obj.file.height,
        )
        return mark_safe(to_return)
    display_title.short_description = 'Image details'

    def show_image(self, obj):
        to_return = '<img src="{}" class="ui small image" />'.format(
            obj.file.url
        )
        return mark_safe(to_return)
    show_image.short_description = 'Thumbnail'


class PdfUploadAdmin(CompareVersionAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields ={'slug': ('title',),}


class OtherUploadAdmin(CompareVersionAdmin):
    list_display = ['title', 'slug', 'extension']
    prepopulated_fields ={'slug': ('title',),}


admin.site.register(ImageUpload, ImageUploadAdmin)
editor_site.register(ImageUpload, ImageUploadAdmin)

admin.site.register(OtherUpload, OtherUploadAdmin)
editor_site.register(OtherUpload, OtherUploadAdmin)

admin.site.register(PdfUpload, PdfUploadAdmin)
editor_site.register(PdfUpload, PdfUploadAdmin)
