
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


@register.filter
def joinby(value, arg):
    return arg.join(value)


@register.filter
def get_type(value):
    return value.__class__.__name__


@register.filter
def intiger(value):
    return int(value)


'''@register.filter
def float(value):
    return int(float)'''


@register.filter
def get_key(obj, key):
    return obj[key][0]
