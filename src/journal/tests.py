from datetime import date

from django.test import TestCase

from journal.models import *


class ArticleTestCase(TestCase):
    def test_article_interview_markdown(self):
        category = Category.objects.create(
            name='Category',
            slug='category',
        )
        article = Article.objects.create(
            title='Article',
            slug='article',
            subtitle='**subtitle**',
            content='~A1 Quote\n~B2 Quote2',
            date=date(2024, 8, 22),
            category=category,
        )
        self.assertEquals(article.formatted_subtitle, '<p><strong>subtitle</strong></p>')
        self.assertEquals(article.formatted_content, '<p><span class="interview-quote author-1">A</span>Quote<br>\n~B2 Quote2</p>')
