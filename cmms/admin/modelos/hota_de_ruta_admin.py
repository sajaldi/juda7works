


from django.contrib import admin
from ...models import Area, HojaDeRuta, PasosHojaDeRuta




class PasosHojaDeRutaInline(admin.TabularInline):
    model = PasosHojaDeRuta
    extra = 1  # Número de filas adicionales para agregar pasos
    fields = ('paso','tiempo')  # Campos que se mostrarán en la tabla

class HojaDeRutaInline(admin.TabularInline):
    model = HojaDeRuta
    fields = ('nombre','intervalo','horario')
    extra =1
@admin.register(HojaDeRuta)
class HojaDeRutaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    inlines = [PasosHojaDeRutaInline]
    readonly_fields = ('total_duracion_en_minutos', 'total_duracion_en_horas')
    def total_duracion_en_minutos(self, obj):
        if obj.horario:
            return obj.horario.total_duracion_en_minutos
        return None
    total_duracion_en_minutos.short_description = 'Total Duración en Minutos'

    def total_duracion_en_horas(self, obj):
        if obj.horario:
            return obj.horario.total_duracion_en_horas
        return None
    total_duracion_en_horas.short_description = 'Total Duración en Horas'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "areas":
            kwargs["queryset"] = Area.objects.filter(principal = None)
        return super().formfield_for_manytomany(db_field, request, **kwargs)
