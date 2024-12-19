from django import template

register = template.Library()


@register.filter
def float_add(value, arg):
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value
