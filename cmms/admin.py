from django.contrib import admin
from .models import Activo  # Import Activos model

from .admin.modelos import *

from .admin.modelos.activo_admin import ActivoAdmin
from .admin.modelos.hota_de_ruta_admin import HojaDeRutaAdmin
from .admin.modelos.plan_de_mantenimiento_admin import PlanDeMantenimientoAdmin
from .admin.modelos.frecuencia_admin import FrecuenciaAdmin



@admin.register(Frecuencia)
class FrecuenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'intervalo', 'color')  # Incluye 'intervalo'
    list_editable = ('intervalo', )                 # Define 'intervalo' como editable
    search_fields = ('nombre', )          















