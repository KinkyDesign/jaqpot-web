from django import template

register = template.Library()

@register.filter(name='private')
def private(obj, attribute):
    return getattr(obj, attribute)

@register.filter
def get_range( value ):
    return range(1, value+1)

@register.filter
def split(string, sep):
    """Return the last string split by sep.

    Example usage: {{ value|split:"/" }}
    """
    return string.split(sep)[1]