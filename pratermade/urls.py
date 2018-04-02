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
from website.views import IndexView, GenericView, ElementsView, ArticleView, ArticleEditView, TocView, PageView, \
    ImageUpload
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

# Add this back to re-enable the admin side.
# path('admin/', admin.site.urls),


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.login, name='login'),
    path('accounts/logout/', auth_views.logout, name='logout'),
    url(r'accounts/resetpw/',auth_views.password_reset,
        {'post_reset_redirect' : '/accounts/resetpwdone/'},
        name="password_reset"),
    path(r'', IndexView.as_view(), name="index"),
    path(r'generic/', GenericView.as_view(), name="generic"),
    path(r'elements/', ElementsView.as_view(), name="elements"),
    url(r'article/(?P<slug>[a-zA-Z0-9\-_]+)/$', ArticleView.as_view(), name="article"),
    url(r'editArticle/(?P<slug>[a-zA-Z0-9\-_]+)/$', ArticleEditView.as_view(), name="edit_article"),
    url(r'toc/(?P<slug>[a-zA-Z0-9\-_]+)/$', TocView.as_view(), name="toc"),
    url(r'page/(?P<slug>[a-zA-Z0-9\-_]+)/$', PageView.as_view(), name="page"),
    url(r'imageupload/(?P<slug>[a-zA-Z0-9\-_]+)/$', ImageUpload.as_view(), name="imageupload"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

