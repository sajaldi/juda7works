# filepath: /C:/Django/SoftCoMJuda/Softcom/cmms/urls.py
from django.urls import path

from cmms.admin.modelos.sistema_admin import importar_sistemas_excel
from views.puesto_views import gestionar_puestos
from views.sistemas_view import exportar_plantilla_sistemas, importar_sistemas_view
from .admin.modelos.puesto_admin import *
from views.area_views import exportar_plantilla_areas, importar_areas_view
from views.herramientas_view import exportar_plantilla_herramientas, importar_herramientas_view


 
from .acciones import exportar_plantilla_activos, exportar_plantilla_pasos, importar_activos_view
from views.hoja_de_ruta_views import exportar_plantilla_hojaderuta, importar_plantilla_hojaderuta
from .views import  import_view, export_view, exportar_pasos_hoja_de_ruta, get_activos_por_categoria, importar_pasos_hoja_de_ruta, menu, obtener_ordenes, ordenes_por_fecha, programacion_view, vista_activos_por_dia, vista_anual, vista_anual_filtrada, vista_mensual, plantilla_sistema, vista_activos


urlpatterns = [
    ## URLS de la aplicación CMMS
    ## Plantilla de Vista anual
    path('vista_anual/', vista_anual, name='vista_anual'), # Asocia la vista a la URL de Vista Anual
    path('vista_mensual/<str:fecha_inicio>/', vista_mensual, name='vista_mensual'),
     path('vista_anual_filtrada/', vista_anual_filtrada, name='vista_anual_filtrada'), # Asocia la vista a la URL de Vista Mensual
    # Activos
    path("exportar-plantilla/",exportar_plantilla_activos, name="exportar_plantilla"),  #
    path("importar-activos/", importar_activos_view, name="importar_activos"),
    path('admin/get_activos_por_categoria/', get_activos_por_categoria, name="get_activos_por_categoria"),
    path('vista_activos/', vista_activos, name='vista_activos'),
    path('activos-dia/<str:fecha_inicio>/', vista_activos_por_dia, name='activos_por_dia'),
    # Hoja de Ruta
    path('exportar-plantilla-hojaderuta/', exportar_plantilla_hojaderuta, 
         name='exportar_plantilla_hojaderuta'),# Asocia la vista a la URL de Exportar Plantilla de Hoja de Ruta
    path('importar-plantilla-hojaderuta/', importar_plantilla_hojaderuta, 
         name='importar_plantilla_hojaderuta'),
    # Pasos de Hoja de Ruta
    path("exportar_pasos/", exportar_pasos_hoja_de_ruta, name="exportar_pasos"),
    path("importar_pasos/", importar_pasos_hoja_de_ruta, name="importar_pasos"),
    # Ordenes
    path('ordenes/semana/<int:semana>/', ordenes_por_fecha, name='ordenes_por_fecha'),
    path('cmms/obtener_ordenes/', obtener_ordenes, name='obtener_ordenes'),
    #Sistema   
    path('plantilla_sistema/', exportar_plantilla_sistemas, name='exportar_plantilla_sistemas'), # Asocia la vista a la URL de Plantilla de Sistema
    path('importar_sistemas/', importar_sistemas_view, name='importar_sistemas_view'),
    # Herramientas
    path('importar_herramientas/', importar_herramientas_view, name='importar_herramientas'),
    path("exportar_herramientas/", exportar_plantilla_herramientas, name="exportar_plantilla_herramientas"),
    # Menu
    path('menu', menu, name='cmms_menu'),  
    
    path('exportar_area', exportar_plantilla_areas, name='exportar_plantilla_areas'),
    path('importar_areas', importar_areas_view, name='importar_areas'),
path('gestionar_puestos/', gestionar_puestos, name='gestionar_puestos'),
 path('programacion/', programacion_view, name='programacion_form'),
     path("export/", export_view, name="export_excel"),
    path("import/", import_view, name="import_excel"),
   
]