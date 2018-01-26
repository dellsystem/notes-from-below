import markdown

from uploads.models import PdfUpload


EMBED_RE = r'\[pdf:([^\]]+)\]'
class EmbedPattern(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        slug = self.unescape(m.group(2))
        pdf_upload = PdfUpload.objects.filter(slug=slug).first()
        if pdf_upload:
            object_el = markdown.util.etree.Element('object')
            path = pdf_upload.file.url
            object_el.set('data', path)
            object_el.set('type', 'application/pdf')
            object_el.set('width', '100%')
            object_el.set('height', '800px')
            iframe_el = markdown.util.etree.SubElement(object_el, "iframe")
            iframe_el.set('src', path)
            iframe_el.set('width', '100%')
            iframe_el.set('height', '800px')
            iframe_el.text = 'Please download the PDF'
            return object_el
        else:
            return 'INVALID FILE: ' + slug


class EmbedExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['embed'] = EmbedPattern(EMBED_RE, md)


def makeExtension(*args, **kwargs):
    return EmbedExtension(*args, **kwargs)
