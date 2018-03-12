from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Article
from django.shortcuts import get_object_or_404
# Create your views here.


class IndexView(TemplateView):
    template_name = "index.html"

class GenericView(TemplateView):
    template_name = "generic.html"

class ElementsView(TemplateView):
    template_name = "elements.html"

class ArticleView(TemplateView):
    template_name = "generic.html"

    def get_context_data(self, **kwargs):
        context = super(ArticleView, self).get_context_data(**kwargs)
        context['article'] = get_object_or_404(Article, slug=self.kwargs['slug'])
        return context

