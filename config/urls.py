"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from .sitemaps import (
    HomeSitemap,
    StaticViewSitemap,
    PortfolioSitemap,
)

from apps.users.views import portfolio_seo_view, static_page_seo_view

sitemaps = {
    "home": HomeSitemap,
    "static": StaticViewSitemap,
    "portfolio": PortfolioSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),

    path("api/auth/", include("apps.users.urls")),
    path("api/projects/", include("apps.projects.urls")),
    path("api/certificates/", include("apps.certificates.urls")),

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    path('login/', static_page_seo_view, name='login_seo'),
    path('register/', static_page_seo_view, name='register_seo'),
    path('about/', static_page_seo_view, name='about_seo'),
    path('', static_page_seo_view, name='home_seo'),

    path('<str:username>/', portfolio_seo_view, name='portfolio_seo'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)