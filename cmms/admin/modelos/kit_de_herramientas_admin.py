

from django.contrib import admin
from ...models import KitDeHerramientas, Herramienta


@admin.register(KitDeHerramientas)
class KitDeHerramientasAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion',)
    search_fields = ('nombre', 'descripcion')
  
    ordering = ('nombre',)




@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ('nombre',  'descripcion', 'marca')
    search_fields = ('nombre', 'marca')
    list_filter = ('marca',)

