


from django import forms
from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib import admin
from ...models import Area, HojaDeRuta, PasosHojaDeRuta, Sistema, Programacion

from django.utils import timezone
from datetime import datetime

class AreaSelectionForm(forms.Form):
    area = forms.ModelChoiceField(
        queryset=Area.objects.filter(principal=None),
        label="Área Principal",
        help_text="Seleccione el área principal para crear las programaciones"
    )


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
    fields = ('nombre','intervalo',)
    extra =1
@admin.register(HojaDeRuta)
class HojaDeRutaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion','intervalo','sistema',)
    search_fields = ('nombre', 'descripcion')
    list_filter = (SistemaPrincipalFilter, 'intervalo', 'sistema', )
    ordering = ('nombre',)
    inlines = [PasosHojaDeRutaInline]
   





    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "areas":
            kwargs["queryset"] = Area.objects.filter(principal = None)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    actions = ['crear_programaciones']

    def crear_programaciones(self, request, queryset):
        if 'apply' in request.POST:
            area_id = request.POST.get('area')
            area_principal = Area.objects.get(id=area_id)
            areas_hijas = Area.objects.filter(principal=area_principal)
            
            current_year = timezone.now().year
            end_of_year = timezone.make_aware(datetime(current_year, 12, 31, 23, 59, 59))

            programaciones_creadas = 0
            for hoja_ruta in queryset:
                # Create one Programacion per HojaDeRuta
                prog = Programacion.objects.create(
                    nombre=f"Programación {hoja_ruta.nombre} - {area_principal.nombre}",
                    HojaDeRuta=hoja_ruta,
                    programado=False,
                    fecha_final=end_of_year
                )
                # Add all child areas to this Programacion
                prog.areas.add(*areas_hijas)
                programaciones_creadas += 1
            
            self.message_user(
                request,
                f"Se crearon {programaciones_creadas} programaciones exitosamente.",
                messages.SUCCESS
            )
            return HttpResponseRedirect(request.get_full_path())

        form = AreaSelectionForm()
        return render(
            request,
            'admin/crear_programaciones.html',
            context={
                'title': 'Seleccionar Área para Programaciones',
                'hojas': queryset,
                'form': form,
                'action': 'crear_programaciones'
            }
        )

    crear_programaciones.short_description = "Crear programaciones para las hojas seleccionadas"
