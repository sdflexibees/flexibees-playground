from django import template
from flexibees_finance.settings import base

register = template.Library()

@register.simple_tag
def get_constant(constant_name):
    return getattr(base, constant_name, '')