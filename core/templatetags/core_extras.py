from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Allow dict lookups by variable key in templates: {{ mydict|get_item:key }}"""
    if not dictionary:
        return None
    return dictionary.get(key)
