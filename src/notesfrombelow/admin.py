from django.contrib import admin


class EditorAdmin(admin.AdminSite):
    site_header = 'Notes From Below - Editor'
    index_template = 'admin_index.html'


editor_site = EditorAdmin(name='editor')
admin.site.site_header = 'Notes From Below - SUDO'
