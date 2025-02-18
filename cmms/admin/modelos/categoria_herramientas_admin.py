from django.contrib import admin



from ...models import CategoriaHerramienta


@admin.register(CategoriaHerramienta)
class CategoriaHerramientaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

