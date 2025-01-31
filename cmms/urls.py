# filepath: /C:/Django/SoftCoMJuda/Softcom/cmms/urls.py
from django.urls import path
from views.hoja_de_ruta_views import exportar_plantilla_hojaderuta, importar_plantilla_hojaderuta
from .views import vista_anual, vista_mensual, exportar_plantilla_sistema, plantilla_sistema


urlpatterns = [
    path('vista_anual/', vista_anual, name='vista_anual'),
    path('vista_mensual/<str:fecha_inicio>/', vista_mensual, name='vista_mensual'),
    path('exportar-plantilla-sistema/', exportar_plantilla_sistema, name='exportar_plantilla_sistema'),
    path('plantilla_sistema/', plantilla_sistema, name='plantilla_sistema'),
    path('exportar-plantilla-hojaderuta/', exportar_plantilla_hojaderuta, name='exportar_plantilla_hojaderuta'),
    path('importar-plantilla-hojaderuta/', importar_plantilla_hojaderuta, name='importar_plantilla_hojaderuta'),
]