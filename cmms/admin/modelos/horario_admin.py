

from django.contrib import admin

from ...models import DiaHorario, HorarioPreestablecido


class DiaHorarioInline(admin.TabularInline):
    model = DiaHorario
    extra = 1  # Mostrar un formulario adicional vacío
@admin.register(HorarioPreestablecido)
class HorarioPreestablecidoAdmin(admin.ModelAdmin):
    list_display = ('nombre','total_duracion_en_minutos','total_duracion_en_horas')  # Muestra solo el nombre del horario
    inlines = [DiaHorarioInline]  # Agrega los días como una sección en línea

    # Solución para `list_filter`
    def get_dias_semana_filters(self, request):
        # Personaliza el filtro si es necesario
        return super().get_dias_semana_filters(request)
