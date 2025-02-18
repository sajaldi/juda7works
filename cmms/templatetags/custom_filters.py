from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    if isinstance(dictionary, dict):  # Verifica si es un diccionario
        return dictionary.get(key, '')
    return ''  # Retorna cadena vacía si no es un diccionario

