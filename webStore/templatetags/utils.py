from django import template

register = template.Library()

@register.filter
def classname(obj):
    """Returns the class name of the widget."""
    return obj.__class__.__name__

