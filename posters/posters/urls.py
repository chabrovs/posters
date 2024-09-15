"""
URL configuration for posters project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.conf import settings
import debug_toolbar
# NOTE: Add in production!
from django.conf.urls.static import static
from django.views.static import serve
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    # NOTE: Uncomment in production!
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
    # path('posters/', include(('posters_app.urls', 'posters_app'), namespace='posters_app')),
    # path('user_account/', include(('user_account_app.urls', 'user_account_app'), namespace='user_account_app')),
    path('i18n/', include('django.conf.urls.i18n')),
    # path('user_auth/', include("django.contrib.auth.urls")),
]


urlpatterns += i18n_patterns (
    path('posters/', include(('posters_app.urls', 'posters_app'), namespace='posters_app')),
    path('user_account/', include(('user_account_app.urls', 'user_account_app'), namespace='user_account_app')),
)

# NOTE: Comment in Production!
if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r'^rosetta/', include('rosetta.urls'))
    ]