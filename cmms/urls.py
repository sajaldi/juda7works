# filepath: /C:/Django/SoftCoMJuda/Softcom/cmms/urls.py
from django.urls import path

from cmms.admin.modelos.sistema_admin import importar_sistemas_excel


 
from .acciones import exportar_plantilla_activos, exportar_plantilla_pasos, importar_activos_view
from views.hoja_de_ruta_views import exportar_plantilla_hojaderuta, importar_plantilla_hojaderuta
from .views import exportar_pasos_hoja_de_ruta, get_activos_por_categoria, importar_pasos_hoja_de_ruta, menu, obtener_ordenes, ordenes_por_fecha, vista_activos_por_dia, vista_anual, vista_mensual, plantilla_sistema, vista_activos


urlpatterns = [
    path('vista_anual/', vista_anual, name='vista_anual'),
    path('vista_mensual/<str:fecha_inicio>/', vista_mensual, name='vista_mensual'),
    path('plantilla_sistema/', plantilla_sistema, name='plantilla_sistema'),
    path('exportar-plantilla-hojaderuta/', exportar_plantilla_hojaderuta, name='exportar_plantilla_hojaderuta'),
    path('importar-plantilla-hojaderuta/', importar_plantilla_hojaderuta, name='importar_plantilla_hojaderuta'),
    path("exportar-plantilla/",exportar_plantilla_activos, name="exportar_plantilla"),
    path("importar-activos/", importar_activos_view, name="importar_activos"),
    path('admin/get_activos_por_categoria/', get_activos_por_categoria, name="get_activos_por_categoria"),
    path('vista_activos/', vista_activos, name='vista_activos'),
    path('cmms/obtener_ordenes/', obtener_ordenes, name='obtener_ordenes'),
    path('activos-dia/<str:fecha_inicio>/', vista_activos_por_dia, name='activos_por_dia'),
    path("exportar_pasos/", exportar_pasos_hoja_de_ruta, name="exportar_pasos"),
    path("importar_pasos/", importar_pasos_hoja_de_ruta, name="importar_pasos"),
    path('menu', menu, name='cmms_menu'),  # Asocia la vista a la URL
    path('ordenes/semana/<int:semana>/', ordenes_por_fecha, name='ordenes_por_fecha'),
    path('importar_sistemas/', importar_sistemas_excel, name='importar_sistemas'),


]