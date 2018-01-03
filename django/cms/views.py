from django.shortcuts import render
from django.views import generic

from .models import Page


class PageView(generic.DetailView):
    model = Page
    template_name = 'page.html'
