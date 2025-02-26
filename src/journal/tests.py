from datetime import date
import mock

from django.test import TestCase

from journal.models import *
from journal.utils import find_similar_articles


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
        self.assertEqual(article.formatted_subtitle, '<p><strong>subtitle</strong></p>')
        self.assertEqual(article.formatted_content, '<p><span class="interview-quote author-1">A</span>Quote<br>\n~B2 Quote2</p>')

    def test_find_similar_articles(self):
        article_1 = mock.Mock(unformatted_content='this is about cars', name='1')
        article_2 = mock.Mock(unformatted_content='also about cars i love cars really cars', name='2')
        article_3 = mock.Mock(unformatted_content='this is about boats', name='3')
        article_4 = mock.Mock(unformatted_content='this one is also about boats boats boats i love boats', name='4')
        article_5 = mock.Mock(unformatted_content='nothing blah', name='5')
        article_6 = mock.Mock(unformatted_content='blah blah blah blah blah blah blah blah blah blah blah blah blah blah nothing', name='6')
        article_7 = mock.Mock(unformatted_content='this one is really long and contains a lot of words but it should not show up just because there is some intersection about', name='7')
        articles = [
            article_1, article_2, article_3, article_4, article_5, article_6, article_7
        ]

        self.assertEqual(find_similar_articles('about cars', articles), (article_2, article_1), 'cars')
        self.assertEqual(find_similar_articles('about boats', articles), (article_4, article_3), 'boats')
        self.assertEqual(find_similar_articles('nothing', articles), (article_5, article_6), 'nothing')
        self.assertEqual(find_similar_articles('blah', articles), (article_6, article_5), 'blah')
