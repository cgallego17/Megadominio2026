from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.services.models import Service


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return [
            'core:home',
            'core:services',
            'core:about',
            'core:contact',
            'core:store',
            'core:coffee',
            'core:quote_request',
        ]

    def location(self, item):
        return reverse(item)

    def get_priority(self, item):
        if item == 'core:home':
            return 1.0
        if item == 'core:services':
            return 0.9
        return 0.7

    priority = get_priority


class ServiceSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Service.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
