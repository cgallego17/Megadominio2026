"""Template tags para el dashboard"""
from django import template

register = template.Library()


@register.filter
def getattr_filter(obj, attr):
    """Obtiene un atributo de un objeto por nombre"""
    return getattr(obj, attr, None)
