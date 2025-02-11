from django.contrib import admin
from .models import Activo  # Import Activos model

from .admin.modelos import *


admin.site.site_header = "Mi Panel de Administración"
admin.site.site_title = "Título del Administrador"
admin.site.index_title = "Bienvenido al Panel de Control"


from .admin.modelos.activo_admin import ActivoAdmin
from .admin.modelos.hota_de_ruta_admin import HojaDeRutaAdmin
from .admin.modelos.plan_de_mantenimiento_admin import PlanDeMantenimientoAdmin
from .admin.modelos.frecuencia_admin import FrecuenciaAdmin
from .admin.modelos.pasos_hoja_de_ruta_admin import PasosHojaDeRutaAdmin

admin.site.register(MenuItem)

from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy as _


@admin.register(Frecuencia)
class FrecuenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'intervalo', 'color')  # Incluye 'intervalo'
    list_editable = ('intervalo', )                 # Define 'intervalo' como editable
    search_fields = ('nombre', )          















