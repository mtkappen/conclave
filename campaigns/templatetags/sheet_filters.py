from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a key."""
    if dictionary is None:
        return None
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)


@register.filter
def safe_dict_get(value, arg):
    """Safely get a value from a dictionary, handling nested access."""
    if not value or not isinstance(value, dict):
        return None
    try:
        return value.get(arg)
    except (AttributeError, TypeError):
        return None


@register.filter
def replace(value, args):
    """Replace occurrences in a string."""
    if not value:
        return value
    try:
        old, new = args.split(':')
        return str(value).replace(old, new)
    except (ValueError, AttributeError):
        return value
