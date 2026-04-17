from django import template

register = template.Library()

@register.filter
def dict(value, arg):
    return value.get(arg)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "")