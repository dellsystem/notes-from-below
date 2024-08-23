import mock

from django.core.files import File
from markdown.test_tools import TestCase as MarkdownTestCase


class TestEmbed(MarkdownTestCase):
    default_kwargs = {
        'extensions': ['uploads.extensions.embed'],
    }
    maxDiff = None

    def test_invalid_pdf(self):
        self.assertMarkdownRenders(
            self.dedent(
                """
                [pdf:hello]
                """
            ),
            self.dedent(
                """
                <p>INVALID FILE: hello</p>
                """
            ),
            output_format='html'
        )

    def test_valid_pdf(self):
        with mock.patch('uploads.models.PdfUpload') as pdf_upload_mock:
            mock_upload = mock.Mock()
            mock_upload.file.url = '/media/pdfs/uploads/url.pdf'
            mock_querylist = mock.Mock()
            mock_querylist.first.return_value = mock_upload
            pdf_upload_mock.objects.filter.return_value = mock_querylist
            self.assertMarkdownRenders(
                self.dedent(
                    """
                    [pdf:hello]
                    """
                ),
                self.dedent(
                    """<p>
<div>
<object class="non-mobile-only" data="/media/pdfs/uploads/url.pdf" height="800px" type="application/pdf" width="100%">
<iframe height="800px" src="/media/pdfs/uploads/url.pdf" width="100%">Please download the PDF</iframe>
</object>
<img class="mobile-only" src="/media/pdfs/uploads/url.pdf.png"><div class="print-only">Don't print this page, print the PDF itself!</div>
</div>
</p>"""
                ),
                output_format='html'
            )

    def test_invalid_image(self):
        self.assertMarkdownRenders(
            self.dedent(
                """
                [img:bye]
                """
            ),
            self.dedent(
                """
                <p>INVALID FILE: bye</p>
                """
            ),
            output_format='html'
        )

    def test_valid_image(self):
        with mock.patch('uploads.models.ImageUpload') as image_upload_mock:
            mock_upload = mock.Mock()
            mock_upload.file.url = '/media/images/uploads/bye.png'
            mock_querylist = mock.Mock()
            mock_querylist.first.return_value = mock_upload
            image_upload_mock.objects.filter.return_value = mock_querylist
            self.assertMarkdownRenders(
                self.dedent(
                    """
                    [img:bye]
                    """
                ),
                self.dedent(
                    """
                    <p>
                    <div class="uploaded-image"><span></span><img src="/media/images/uploads/bye.png"></div>
                    </p>
                    """
                ),
                output_format='html'
            )

    def test_image_with_caption(self):
        with mock.patch('uploads.models.ImageUpload') as image_upload_mock:
            mock_upload = mock.Mock()
            mock_upload.file.url = '/media/images/uploads/bye.png'
            mock_querylist = mock.Mock()
            mock_querylist.first.return_value = mock_upload
            image_upload_mock.objects.filter.return_value = mock_querylist
            self.assertMarkdownRenders(
                self.dedent(
                    """
                    [img:bye Bye]
                    """
                ),
                self.dedent(
                    """
                    <p>
                    <div class="uploaded-image"><span>Bye</span><img src="/media/images/uploads/bye.png"></div>
                    </p>
                    """
                ),
                output_format='html'
            )

    def test_double_image(self):
        with mock.patch('uploads.models.ImageUpload') as image_upload_mock:
            mock_upload_1 = mock.Mock()
            mock_upload_1.file.url = '/media/images/uploads/hello.png'
            mock_upload_2 = mock.Mock()
            mock_upload_2.file.url = '/media/images/uploads/bye.png'
            mock_querylist = mock.Mock()
            mock_querylist.first.side_effect = [mock_upload_1, mock_upload_2]
            image_upload_mock.objects.filter.return_value = mock_querylist
            self.assertMarkdownRenders(
                self.dedent(
                    """
                    [img2:hello bye]
                    """
                ),
                self.dedent(
                    """
                    <p>
                    <div class="uploaded-images"><img src="/media/images/uploads/hello.png"><img src="/media/images/uploads/bye.png"></div>
                    </p>
                    """
                ),
                output_format='html'
            )

    def test_images(self):
        with mock.patch('uploads.models.ImageUpload') as image_upload_mock:
            mock_upload_1 = mock.Mock()
            mock_upload_1.file.url = '/media/images/uploads/one.png'
            mock_upload_2 = mock.Mock()
            mock_upload_2.file.url = '/media/images/uploads/two.png'
            mock_upload_3 = mock.Mock()
            mock_upload_3.file.url = '/media/images/uploads/three.png'
            mock_querylist = mock.Mock()
            mock_querylist.first.side_effect = [
                mock_upload_1, mock_upload_2, mock_upload_3
            ]
            image_upload_mock.objects.filter.return_value = mock_querylist
            self.assertMarkdownRenders(
                self.dedent(
                    """
                    [images:one two three]
                    """
                ),
                self.dedent(
                    """
                    <p>
                    <div class="uploaded-image"><img src="/media/images/uploads/one.png"><img src="/media/images/uploads/two.png"><img src="/media/images/uploads/three.png"></div>
                    </p>
                    """
                ),
                output_format='html'
            )
            image_upload_mock.objects.filter.assert_any_call(slug='one')
            image_upload_mock.objects.filter.assert_any_call(slug='two')
            image_upload_mock.objects.filter.assert_any_call(slug='three')
            self.assertEqual(image_upload_mock.objects.filter.call_count, 3)
