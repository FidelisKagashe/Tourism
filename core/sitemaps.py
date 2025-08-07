from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from tours.models import TourPackage
from parks.models import NationalPark

class TourPackageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return TourPackage.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

class NationalParkSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return NationalPark.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['core:home', 'core:about', 'core:contact', 'core:faq']

    def location(self, item):
        return reverse(item)