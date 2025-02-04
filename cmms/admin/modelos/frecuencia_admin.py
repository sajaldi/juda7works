

from django.contrib import admin

from ...models import DiaHorario, Frecuencia, HorarioPreestablecido

@admin.register(Frecuencia)
class FrecuenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'intervalo', )
    search_fields = ('nombre', )
    
