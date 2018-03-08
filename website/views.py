from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.


class IndexView(TemplateView):
    template_name = "index.html"

class GenericView(TemplateView):
    template_name = "generic.html"

class ElementsView(TemplateView):
    template_name = "elements.html"
