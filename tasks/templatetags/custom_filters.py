from django import template

register = template.Library()

@register.filter
def get_item(dict_list, key):
    for d in dict_list:
        if (
            d.get('complete') == key or 
            d.get('recur_frequency') == key or 
            d.get('priority') == key
        ):
            return d.get('count', 0)
    return 0
