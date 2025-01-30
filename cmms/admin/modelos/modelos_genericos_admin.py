from django.contrib import admin
from ...models import Frecuencia

@admin.register(Frecuencia)
class FrecuenciaAdmin(admin.ModelAdmin):
    list_display=('nombre',)
    list_filter=('nombre',)
    search_fields=('nombre',)
