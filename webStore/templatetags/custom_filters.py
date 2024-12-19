from django import template

register = template.Library()


@register.filter
def float_add(value, arg):
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value


@register.simple_tag(takes_context=True)
def increment(context, name):
    if name not in context:
        context[name] = 0
    context[name] += 1
    return context[name]