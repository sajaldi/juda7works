# filepath: /C:/Django/SoftCoMJuda/Softcom/cmms/urls.py
from django.urls import path

 
from .acciones import exportar_plantilla_activos, importar_activos_view
from views.hoja_de_ruta_views import exportar_plantilla_hojaderuta, importar_plantilla_hojaderuta
from .views import get_activos_por_categoria, obtener_ordenes, vista_anual, vista_mensual, plantilla_sistema, vista_activos


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
]