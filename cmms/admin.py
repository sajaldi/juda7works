from django.contrib import admin
from .models import Activo  # Import Activos model

from .admin.modelos import *

from .admin.modelos.activo_admin import ActivoAdmin
from .admin.modelos.hota_de_ruta_admin import HojaDeRutaAdmin
from .admin.modelos.plan_de_mantenimiento_admin import PlanDeMantenimientoAdmin





