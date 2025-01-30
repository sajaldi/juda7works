# filepath: /C:/Django/SoftCoMJuda/Softcom/cmms/views.py
from django.shortcuts import render
from datetime import datetime, timedelta
from .models import OrdenDeTrabajo
import logging

# Configurar el logger
logger = logging.getLogger(__name__)

def vista_anual(request):
    # Obtener el año actual
    year = datetime.now().year

    # Crear una lista de semanas del año
    semanas = []
    start_date = datetime(year, 1, 1)
    while start_date.weekday() != 0:
        start_date += timedelta(days=1)
    for week_num in range(1, 53):
        end_date = start_date + timedelta(days=6)
        semanas.append((week_num, start_date, end_date))
        start_date = end_date + timedelta(days=1)

    # Obtener todas las órdenes de trabajo del año
    ordenes = OrdenDeTrabajo.objects.filter(fechaDeInicio__year=year)
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
            ordenes_por_sistema[sistema][hoja_de_ruta] = {'horario': horario, 'semanas': {week_num: [] for week_num in range(1, 53)}}
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
        'semanas': semanas,
        'ordenes_por_sistema': ordenes_por_sistema,
        'niveles_por_semana': niveles_por_semana,
    }
    return render(request, 'cmms/vista_anual.html', context)



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