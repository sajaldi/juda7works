


from django.contrib import admin
from ...models import Area, HojaDeRuta, PasosHojaDeRuta, Sistema




class PasosHojaDeRutaInline(admin.TabularInline):
    model = PasosHojaDeRuta
    extra = 1  # Número de filas adicionales para agregar pasos
    fields = ('paso','tiempo')  # Campos que se mostrarán en la tabla

class SistemaPrincipalFilter(admin.SimpleListFilter):
    title = 'Sistema Principal'
    parameter_name = 'sistema_principal'

    def lookups(self, request, model_admin):
        sistemas_principales = Sistema.objects.filter(principal__isnull=True).distinct()
        return [(sistema.id, sistema.nombre) for sistema in sistemas_principales]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sistema__principal__id=self.value())
        return queryset



class HojaDeRutaInline(admin.TabularInline):
    model = HojaDeRuta
    fields = ('nombre','intervalo','horario')
    extra =1
@admin.register(HojaDeRuta)
class HojaDeRutaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion','intervalo','sistema','horario')
    search_fields = ('nombre', 'descripcion')
    list_filter = (SistemaPrincipalFilter, 'intervalo', 'sistema', 'horario')
    ordering = ('nombre',)
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
