


from django.contrib import admin
from ...models import Unidad


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    display = ('nombre', 'abreviatura', 'descripcion')
