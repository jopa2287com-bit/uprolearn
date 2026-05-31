from django import template

register = template.Library()


@register.filter(name='split')
def split(value, separator=' '):
    """Split a string by separator and return a list."""
    if not value:
        return []
    return value.split(separator)


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get an item from a dictionary by key."""
    if dictionary is None:
        return None
    return dictionary.get(key)
