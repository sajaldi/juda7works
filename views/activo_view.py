import csv
import datetime
from django.http import HttpResponse
from django.shortcuts import render
from models import Activo, OrdenDeTrabajo
from datetime import datetime, timedelta


   # Asegúrate de importar tu modelo

def exportar_plantilla_activos(request):
    """
    Exporta la plantilla de activos en formato CSV con los datos actuales de la base de datos.
    """
    # Configurar la respuesta HTTP como archivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="plantilla_activos_{datetime.datetime.now().strftime("%Y%m%d")}.csv"'

    # Crear el escritor CSV
    writer = csv.writer(response)

    # Escribir la cabecera del archivo
    writer.writerow(['ID', 'Nombre', 'Marca', 'No. Inventario', 'Modelo'])

    # Obtener y escribir los datos existentes
    activos = Activo.objects.all()
    for activo in activos:
        writer.writerow([activo.id, activo.nombre, activo.marca.nombre if activo.marca else "", activo.no_inventario, activo.modelo.nombre if activo.modelo else ""])

    return response
