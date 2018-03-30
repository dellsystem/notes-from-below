from django.contrib import admin

from reversion_compare.admin import CompareVersionAdmin

from notesfrombelow.admin import editor_site
from .models import *


class ImageUploadAdmin(CompareVersionAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields ={'slug': ('title',),}


class PdfUploadAdmin(CompareVersionAdmin):
    list_display = ['title', 'slug', 'png_file']
    prepopulated_fields ={'slug': ('title',),}


admin.site.register(ImageUpload, ImageUploadAdmin)
editor_site.register(ImageUpload, ImageUploadAdmin)

admin.site.register(PdfUpload, PdfUploadAdmin)
editor_site.register(PdfUpload, PdfUploadAdmin)
