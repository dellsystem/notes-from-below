from django.contrib import admin
from django.utils.html import mark_safe

from reversion_compare.admin import CompareVersionAdmin

from notesfrombelow.admin import editor_site
from .models import *


class ImageUploadAdmin(CompareVersionAdmin):
    list_display = ['display_title', 'get_dimensions', 'show_image']
    prepopulated_fields ={'slug': ('title',),}

    def display_title(self, obj):
        to_return = '<h1 class="ui header">{title}<div class="sub header">{slug}</div></h1>'.format(
            title=obj.title,
            slug=obj.slug,
        )
        return mark_safe(to_return)
    display_title.short_description = 'Image details'

    def get_dimensions(self, obj):
        return '{width} x {height}'.format(
            width=obj.file.width,
            height=obj.file.height,
        )

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
