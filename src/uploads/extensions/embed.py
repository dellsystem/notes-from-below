from django.utils.html import escape
import markdown
import xml.etree.ElementTree as etree

import uploads.models


EMBED_RE = r'\[(pdf|img|file):([a-z0-9-]+) ?([^\]]*)\]'
#PDF_EMBED_RE = r'\[pdf:([a-z0-9-]+) ?([^\]]*)\]'
class EmbedPattern(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        embed_type = m.group(2)
        slug = self.unescape(m.group(3))
        caption = self.unescape(m.group(4))
        if embed_type == 'pdf':
            pdf_upload = uploads.models.PdfUpload.objects.filter(slug=slug).first()
            if pdf_upload:
                # This div structure is messy because it forces the enclosing
                # <p> to close first. Ideally, we'd make this a block pattern.
                div_el = etree.Element('div')
                object_el = etree.SubElement(div_el, 'object')
                path = pdf_upload.file.url
                object_el.set('data', path)
                object_el.set('type', 'application/pdf')
                object_el.set('width', '100%')
                object_el.set('height', '800px')
                iframe_el = etree.SubElement(object_el, "iframe")
                iframe_el.set('src', path)
                iframe_el.set('width', '100%')
                iframe_el.set('height', '800px')
                iframe_el.text = 'Please download the PDF'

                # Show the PNG version for a mobile fallback.
                image_el = etree.SubElement(div_el, 'img')
                image_el.set('class', 'mobile-only')
                object_el.set('class', 'non-mobile-only')
                image_el.set('src', path + '.png')

                print_el = etree.SubElement(div_el, 'div')
                print_el.set('class', 'print-only')
                print_el.text = "Don't print this page, print the PDF itself!"

                return div_el
            else:
                return 'INVALID FILE: ' + slug
        elif embed_type == 'img':
            image_upload = uploads.models.ImageUpload.objects.filter(slug=slug).first()
            if image_upload:
                div_el = etree.Element('div')
                div_el.set('class' , 'uploaded-image')
                span_el = etree.SubElement(div_el, 'span')
                span_el.text = caption
                image_el = etree.SubElement(div_el, 'img')
                image_el.set('src', image_upload.file.url)
                image_el.set('alt', image_upload.alt)
                return div_el
            else:
                return 'INVALID FILE: ' + slug
        else:
            other_upload = uploads.models.OtherUpload.objects.filter(slug=slug).first()
            if other_upload:
                div_el = etree.Element('div')
                div_el.set('class', 'uploaded-file')
                a_el = etree.SubElement(div_el, 'a')
                a_el.set('class', 'ui large red icon button')
                a_el.set('href', other_upload.file.url)
                i_el = etree.SubElement(a_el, 'i')
                i_el.set('class', 'download icon')
                # Using .tail not .text to ensure that it follows the <i>
                i_el.tail = 'Download {title} ({ext})'.format(
                    title=escape(other_upload.title),
                    ext=other_upload.extension
                )
                return div_el
            else:
                return 'INVALID FILE: ' + slug


# For embedding two images side by side.
DOUBLE_EMBED_RE = r'\[img2:([a-z0-9-]+) ([a-z0-9-]+)\]'
class DoubleEmbedPattern(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        slug_1 = self.unescape(m.group(2))
        slug_2 = self.unescape(m.group(3))
        image_1 = uploads.models.ImageUpload.objects.filter(slug=slug_1).first()
        image_2 = uploads.models.ImageUpload.objects.filter(slug=slug_2).first()
        if image_1 and image_2:
            div_el = etree.Element('div')
            div_el.set('class' , 'uploaded-images')
            image_el_1 = etree.SubElement(div_el, 'img')
            image_el_1.set('src', image_1.file.url)
            image_el_1.set('alt', image_1.alt)
            image_el_2 = etree.SubElement(div_el, 'img')
            image_el_2.set('src', image_2.file.url)
            image_el_2.set('alt', image_2.alt)
            return div_el
        else:
            invalid_slugs = []
            if not image_1:
                invalid_slugs.append(slug_1)
            if not image_2:
                invalid_slugs.append(slug_2)
            return 'INVALID FILE: ' + ', '.join(invalid_slugs)


# For embedding 2+ images side by side. Will eventually supersede Double
IMAGE_EMBED_RE = r'\[images:([a-z0-9- ]+)\]'
class ImageEmbedPattern(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        div_el = etree.Element('div')
        div_el.set('class' , 'uploaded-image')

        slugs = self.unescape(m.group(2)).split()
        for slug in slugs:
            image = uploads.models.ImageUpload.objects.filter(slug=slug).first()

            # Might want to do this asynchronously to catch all the invalids
            if not image:
                return 'INVALID FILE: {}'.format(image)

            image_el = etree.SubElement(div_el, 'img')
            image_el.set('src', image.file.url)
            image_el.set('alt', image.alt)

        return div_el


class EmbedExtension(markdown.Extension):
    def extendMarkdown(self, md):
        # A recent Markdown update changed the syntax for registering new inline patterns. I'm only guessing here. The last parameter is a priority number I guess
        md.inlinePatterns.register(EmbedPattern(EMBED_RE, md), 'embed', 175)
        md.inlinePatterns.register(DoubleEmbedPattern(DOUBLE_EMBED_RE, md), 'double_embed', 176)
        md.inlinePatterns.register(ImageEmbedPattern(IMAGE_EMBED_RE, md), 'image_embed', 177)


def makeExtension(*args, **kwargs):
    return EmbedExtension(*args, **kwargs)
