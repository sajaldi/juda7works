from django import template

register = template.Library()

@register.filter(name='concat_keys')
def concat_keys(sistema_principal, sistema, hoja_de_ruta, week_num):
    """Concatenates sistema_principal, sistema, hoja_de_ruta, and week_num into a string key."""
    return f"{sistema_principal},{sistema},{hoja_de_ruta},{week_num}"