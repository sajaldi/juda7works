# filepath: /C:/Django/SoftCoMJuda/Softcom/cmms/views.py
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta

from openpyxl import Workbook, load_workbook
from .models import HojaDeRuta, OrdenDeTrabajo, Sistema
import logging

# Configurar el logger
logger = logging.getLogger(__name__)


from datetime import datetime, timedelta


def vista_anual(request):
    # Obtener el año actual
    year = datetime.now().year

    months = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'), 
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'), 
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]

    # Crear una lista de semanas del año
    semanas = []
    start_date = datetime(year, 1, 1)
    while start_date.weekday() != 0:  # Asegurar que empiece en lunes
        start_date += timedelta(days=1)
    for week_num in range(1, 53):
        end_date = start_date + timedelta(days=6)
        semanas.append((week_num, start_date, end_date))
        start_date = end_date + timedelta(days=1)

    # Obtener la semana actual
    fecha_actual = datetime.now()
    semana_actual = None
    for week_num, start_date, end_date in semanas:
        if start_date <= fecha_actual <= end_date:
            semana_actual = week_num
            break

    # Obtener todas las órdenes de trabajo del año
    ordenes = OrdenDeTrabajo.objects.filter(fechaDeInicio__year=year)
    logger.debug(f"Total de órdenes encontradas: {len(ordenes)}")

    # Organizar las órdenes por sistema, hoja de ruta y semana
    ordenes_por_sistema = {}
    for orden in ordenes:
        sistema = orden.HojaDeRuta.sistema
        sistema_principal = sistema.principal if sistema.principal else "Sin Sistema Principal"
        hoja_de_ruta = orden.HojaDeRuta.nombre
        horario = orden.HojaDeRuta.horario
        color = orden.HojaDeRuta.intervalo.color

        if sistema_principal not in ordenes_por_sistema:
            ordenes_por_sistema[sistema_principal] = {}
        if sistema not in ordenes_por_sistema[sistema_principal]:
            ordenes_por_sistema[sistema_principal][sistema] = {}
        if hoja_de_ruta not in ordenes_por_sistema[sistema_principal][sistema]:
            ordenes_por_sistema[sistema_principal][sistema][hoja_de_ruta] = {
                'horario': horario,
                'color': color,
                'semanas': {week_num: [] for week_num in range(1, 53)}
            }
        for week_num, start_date, end_date in semanas:
            if start_date <= orden.fechaDeInicio.replace(tzinfo=None) <= end_date:
                ordenes_por_sistema[sistema_principal][sistema][hoja_de_ruta]['semanas'][week_num].append(orden)
                break

    # Calcular el primer y último nivel programado de la semana
    niveles_por_semana = {}
    for sistema_principal, sistemas in ordenes_por_sistema.items():
        for sistema, hojas_de_ruta in sistemas.items():
            for hoja_de_ruta, data in hojas_de_ruta.items():
                for week_num, ordenes in data['semanas'].items():
                    if ordenes:
                        niveles = [orden.area.nombre for orden in ordenes]
                        key = f"{sistema_principal},{sistema},{hoja_de_ruta},{week_num}"
                        niveles_por_semana[key] = {
                            'niveles': f"{niveles[0]}-{niveles[-1]}",
                            'color': data['color']
                        }
                        logger.debug(f"Semana {week_num}: {niveles_por_semana[key]}")

    context = {
        'year': year,
        'semanas': semanas,
        'ordenes_por_sistema': ordenes_por_sistema,
        'niveles_por_semana': niveles_por_semana,
        'semana_actual': semana_actual,  # Pasar la semana actual al contexto
        'months': months,  # Add months to context
    }
    return render(request, 'cmms/vista_anual.html', context)

def obtener_ordenes(request):
    sistema_principal = request.GET.get('sistema_principal')
    sistema = request.GET.get('sistema')
    hoja_de_ruta = request.GET.get('hoja_de_ruta')
    semana = int(request.GET.get('semana'))

    # Obtener el año actual
    year = datetime.now().year

    # Calcular el rango de fechas para la semana específica
    start_date = datetime.strptime(f'{year}-W{str(semana).zfill(2)}-1', "%Y-W%W-%w").date()
    end_date = start_date + timedelta(days=6)

    # Obtener las órdenes asociadas
    ordenes = OrdenDeTrabajo.objects.filter(
        HojaDeRuta__sistema__principal__nombre=sistema_principal,
        HojaDeRuta__sistema__nombre=sistema,
        HojaDeRuta__nombre=hoja_de_ruta,
        fechaDeInicio__range=[start_date, end_date]  # Filtrar por rango de fechas
    )

    # Preparar los datos para el modal
    datos_ordenes = [{
        'nombre': orden.nombre,
        'fechaDeInicio': orden.fechaDeInicio.strftime('%Y-%m-%d %H:%M'),
        'fechaDeFin': orden.fechaDeFin.strftime('%Y-%m-%d %H:%M') if orden.fechaDeFin else 'Sin fecha de fin',
        'area': orden.area.nombre
    } for orden in ordenes]

    return JsonResponse({'ordenes': datos_ordenes})

def vista_mensual(request, fecha_inicio):
    # Convertir la fecha de inicio a un objeto datetime
    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    year = fecha_inicio.year
    month = fecha_inicio.month

    # Crear una lista de semanas del mes
    semanas = []
    start_date = fecha_inicio
    while start_date.weekday() != 0:
        start_date += timedelta(days=1)
    while start_date.month == month:
        end_date = start_date + timedelta(days=6)
        semanas.append((start_date.isocalendar()[1], start_date, end_date))
        start_date = end_date + timedelta(days=1)

    # Obtener todas las órdenes de trabajo del mes
    ordenes = OrdenDeTrabajo.objects.filter(fechaDeInicio__year=year, fechaDeInicio__month=month)
    logger.debug(f"Total de órdenes encontradas: {len(ordenes)}")

    # Organizar las órdenes por sistema, hoja de ruta y semana
    ordenes_por_sistema = {}
    for orden in ordenes:
        sistema = orden.HojaDeRuta.sistema
        hoja_de_ruta = orden.HojaDeRuta.nombre
        horario = orden.HojaDeRuta.horario
        if sistema not in ordenes_por_sistema:
            ordenes_por_sistema[sistema] = {}
        if hoja_de_ruta not in ordenes_por_sistema[sistema]:
            ordenes_por_sistema[sistema][hoja_de_ruta] = {'horario': horario, 'semanas': {week_num: [] for week_num, _, _ in semanas}}
        for week_num, start_date, end_date in semanas:
            if start_date <= orden.fechaDeInicio.replace(tzinfo=None) <= end_date:
                ordenes_por_sistema[sistema][hoja_de_ruta]['semanas'][week_num].append(orden)
                break

    # Calcular el primer y último nivel programado de la semana
    niveles_por_semana = {}
    for sistema, hojas_de_ruta in ordenes_por_sistema.items():
        for hoja_de_ruta, data in hojas_de_ruta.items():
            for week_num, ordenes in data['semanas'].items():
                if ordenes:
                    niveles = [orden.area.nombre for orden in ordenes]
                    key = f"{sistema},{hoja_de_ruta},{week_num}"
                    niveles_por_semana[key] = f"{niveles[0]}-{niveles[-1]}"
                    logger.debug(f"Semana {week_num}: {niveles_por_semana[key]}")

    context = {
        'year': year,
        'month': month,
        'semanas': semanas,
        'ordenes_por_sistema': ordenes_por_sistema,
        'niveles_por_semana': niveles_por_semana,
    }
    return render(request, 'cmms/vista_mensual.html', context)

def exportar_plantilla_sistema(request):
    # Crear un libro de trabajo y una hoja
    wb = Workbook()
    ws = wb.active
    ws.title = "Plantilla de Importación de Sistema"

    # Agregar encabezados
    headers = ["ID", "Nombre", "Principal"]
    ws.append(headers)

    # Obtener los datos del modelo Sistema
    sistemas = Sistema.objects.all()
    for sistema in sistemas:
        principal_nombre = sistema.principal.nombre if sistema.principal else ''
        ws.append([sistema.id, sistema.nombre, principal_nombre])

    # Configurar la respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=plantilla_importacion_sistema.xlsx'

    # Guardar el libro de trabajo en la respuesta
    wb.save(response)
    return response

def plantilla_sistema(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        wb = load_workbook(uploaded_file)
        ws = wb.active

        errores = []

        # Leer los datos del archivo Excel
        for row in ws.iter_rows(min_row=2, values_only=True):
            sistema_id, nombre, principal_nombre = row
            if Sistema.objects.filter(nombre=nombre).exists():
                errores.append(f"El nombre del sistema '{nombre}' ya existe.")
                continue

            if principal_nombre:
                try:
                    principal = Sistema.objects.get(nombre=principal_nombre)
                except Sistema.DoesNotExist:
                    errores.append(f"El sistema principal '{principal_nombre}' no existe.")
                    principal = None
            else:
                principal = None

            # Actualizar o crear el sistema
            Sistema.objects.update_or_create(
                id=sistema_id,
                defaults={'nombre': nombre, 'principal': principal}
            )

        context = {
            'errores': errores,
        }
        return render(request, 'cmms/plantilla_sistema.html', context)

    return render(request, 'cmms/plantilla_sistema.html')

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
@require_http_methods(["POST"])
def mover_ordenes_semana(request):
    try:
        data = json.loads(request.body)
        sistema_principal = data.get('sistema_principal')
        sistema_nombre = data.get('sistema')
        hoja_de_ruta_nombre = data.get('hoja_de_ruta')
        old_week = data.get('old_week')
        new_week = data.get('new_week')
        year = datetime.now().year

        # Calcular fechas de las semanas
        start_date_old = datetime.strptime(f'{year}-W{old_week:02}-1', "%Y-W%W-%w").date()
        start_date_new = datetime.strptime(f'{year}-W{new_week:02}-1', "%Y-W%W-%w").date()

        # Obtener objetos de BD
        sistema = Sistema.objects.get(principal__nombre=sistema_principal, nombre=sistema_nombre)
        hoja_de_ruta = HojaDeRuta.objects.get(sistema=sistema, nombre=hoja_de_ruta_nombre)

        # Obtener órdenes a actualizar
        ordenes = OrdenDeTrabajo.objects.filter(
            HojaDeRuta=hoja_de_ruta,
            fechaDeInicio__year=year,
            fechaDeInicio__week=old_week
        )

        # Actualizar fechas
        for orden in ordenes:
            delta_days = (orden.fechaDeInicio.date() - start_date_old).days
            nueva_fecha_inicio = start_date_new + timedelta(days=delta_days)
            orden.fechaDeInicio = nueva_fecha_inicio
            if orden.fechaDeFin:
                orden.fechaDeFin = nueva_fecha_inicio + (orden.fechaDeFin - orden.fechaDeInicio)
            orden.save()

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)