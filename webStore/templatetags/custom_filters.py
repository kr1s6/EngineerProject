from django import template
import json
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


@register.filter
def load_json(value):
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return []

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})