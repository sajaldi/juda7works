from atexit import register
from django.contrib import admin
from django.urls import path
from django.utils.html import format_html

from ...models import Activo, Categoria, Marca, Modelo

from ...acciones import importar_activos_view

@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'marca', 'no_inventario', 'modelo')
    search_fields = ('nombre', 'marca', 'modelo')
    actions = ['import_assets']

    def import_assets(self, request, queryset):
        return importar_activos_view(request)

    import_assets.short_description = "Importar activos desde CSV/Excel"

    def importar_activos_link(self, obj):
        return format_html('<a class="button" href="importar-activos/">Importar Activos</a>')

    importar_activos_link.short_description = "Importar Activos"
    importar_activos_link.allow_tags = True

    #change_list_template = "admin/activo_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("importar-activos/", self.admin_site.admin_view(importar_activos_view), name="importar-activos"),
        ]
        return custom_urls + urls

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',) 

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


