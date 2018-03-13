"""pratermade URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from website.views import IndexView, GenericView, ElementsView, ArticleView, ArticleEditView
from django.conf.urls.static import static
from django.conf import settings


# Add this back to re-enable the admin side.
# path('admin/', admin.site.urls),


urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'', IndexView.as_view(), name="index"),
    path(r'generic/', GenericView.as_view(), name="generic"),
    path(r'elements/', ElementsView.as_view(), name="elements"),
    url(r'article/(?P<slug>[a-zA-Z0-9]+)/$', ArticleView.as_view(), name="article"),
    url(r'editArticle/(?P<slug>[a-zA-Z0-9]+)/$', ArticleEditView.as_view(), name="edit_article"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

