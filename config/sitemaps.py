from django.contrib.sitemaps import Sitemap
from apps.users.models import Users

class HomeSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"
    protocol = 'https'

    def items(self):
        return [""]

    def location(self, item):
        return "/"

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"
    protocol = 'https'

    def items(self):
        return [
            "/about",
            "/login",
            "/register",
        ]

    def location(self, item):
        return item

class PortfolioSitemap(Sitemap):
    priority = 0.9
    changefreq = "daily"
    protocol = 'https'

    def items(self):
        return Users.objects.filter(
            is_public_portfolio=True
        ).only("username")

    def location(self, obj):
        return f"/{obj.username}"