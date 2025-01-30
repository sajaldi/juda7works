# filepath: /C:/Django/SoftCoMJuda/Softcom/cmms/urls.py
from django.urls import path
from .views import vista_anual, vista_mensual

urlpatterns = [
    path('vista_anual/', vista_anual, name='vista_anual'),
    path('vista_mensual/<str:fecha_inicio>/', vista_mensual, name='vista_mensual'),
]