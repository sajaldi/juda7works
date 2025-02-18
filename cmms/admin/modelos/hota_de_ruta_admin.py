from django import forms
from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from ...models import Area, HojaDeRuta, PasosHojaDeRuta, Sistema, Programacion
from django.utils import timezone
from datetime import datetime
from django.utils.html import format_html


# Formulario para seleccionar un área (acción ya existente)
class AreaSelectionForm(forms.Form):
    area = forms.ModelChoiceField(
        queryset=Area.objects.filter(principal=None),
        label="Área Principal",
        help_text="Seleccione el área principal para crear las programaciones"
    )



class SistemaFilter(admin.SimpleListFilter):
    title = 'Sistema'
    parameter_name = 'sistema'

    def lookups(self, request, model_admin):
        sistema_principal_id = request.GET.get('sistema_principal')
        if sistema_principal_id:
            sistemas = Sistema.objects.filter(principal__id=sistema_principal_id)
        else:
            sistemas = Sistema.objects.all()
        return [(sistema.id, sistema.nombre) for sistema in sistemas]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sistema__id=self.value())
        return queryset
    


# Inline para gestionar los pasos desde la edición de una HojaDeRuta
class PasosHojaDeRutaInline(admin.TabularInline):
    model = PasosHojaDeRuta
    extra = 1  # Muestra una fila adicional para agregar nuevos pasos
    fields = ('paso', 'tiempo')

# Filtro para el sistema principal (ya existente)
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

# Inline para gestionar las Hojas de Ruta (si se utiliza en otro admin)
class HojaDeRutaInline(admin.TabularInline):
    model = HojaDeRuta
    fields = ('nombre', 'intervalo',)
    extra = 1

@admin.register(HojaDeRuta)
class HojaDeRutaAdmin(admin.ModelAdmin):
    list_display = (
        'clave_rutina',
        'sumatoria_tiempo_pasos',
        
        'nombre',
        
        'intervalo',
        'get_subsistema',
        'sistema',
        'ordenamiento',
        
        
    )
    search_fields = ('nombre',)
    # Filtros correctos: se filtra por 'sistema', luego por 'sistema__principal' y 'intervalo'
    list_filter = (
        SistemaPrincipalFilter,
        SistemaFilter,
        'intervalo',
        
    )

    ordering = ('sistema__principal', 'sistema','ordenamiento',)
    
    def get_subsistema(self, obj):
        """
        Devuelve el subsistema (el valor de 'principal' del sistema)
        o None si no existe.
        """
        if obj.sistema and obj.sistema.principal:
            return obj.sistema.principal
        return None
    get_subsistema.short_description = 'Subsistema'
    get_subsistema.admin_order_field = 'sistema__principal'
    
    class Media:
        css = {
            'all': ('css/admin_custom.css',)  # Asegúrate de que este archivo CSS existe en tu carpeta estática
        }

    inlines = [PasosHojaDeRutaInline]  # Inline para crear/editar pasos directamente
    




  

 
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "areas":
            kwargs["queryset"] = Area.objects.filter(principal=None)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    actions = ['crear_programaciones', 'agregar_tres_pasos']

    # Acción ya existente para crear programaciones
    def crear_programaciones(self, request, queryset):
        if 'apply' in request.POST:
            area_id = request.POST.get('area')
            area_principal = Area.objects.get(id=area_id)
            areas_hijas = Area.objects.filter(principal=area_principal)
            
            current_year = timezone.now().year
            end_of_year = timezone.make_aware(datetime(current_year, 12, 31, 23, 59, 59))

            programaciones_creadas = 0
            for hoja_ruta in queryset:
                prog = Programacion.objects.create(
                    nombre=f"Programación {hoja_ruta.nombre} - {area_principal.nombre}",
                    HojaDeRuta=hoja_ruta,
                    programado=False,
                    fecha_final=end_of_year
                )
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

    # Nueva acción: Agregar 3 pasos fijos (Paso 1, Paso 2 y Paso 3, cada uno con tiempo 1)
    def agregar_tres_pasos(self, request, queryset):
        steps = ["Paso 1", "Paso 2", "Paso 3", "Paso 4","Paso 5"]
        added_steps_count = 0
        for hoja in queryset:
            for step in steps:
                # get_or_create intenta obtener el objeto; si no existe, lo crea con los defaults
                obj, created = PasosHojaDeRuta.objects.get_or_create(
                    paso=step,
                    hojaderuta=hoja,
                    defaults={'tiempo': 1}
                )
                if created:
                    added_steps_count += 1

        self.message_user(
            request,
            f"Se han agregado {added_steps_count} pasos nuevos a las hojas de ruta seleccionadas.",
            messages.SUCCESS
        )

