from django.shortcuts import render
from django.views import generic

from .models import Article, Category, Author


class ArticleView(generic.DetailView):
    model = Article
    template_name = 'article.html'


class CategoryView(generic.DetailView):
    model = Category
    template_name = 'category.html'


class AuthorView(generic.DetailView):
    model = Author
    template_name = 'author.html'
