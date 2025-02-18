from collections import defaultdict
from datetime import datetime, timedelta
from django import forms
from django.contrib import admin
from django.shortcuts import render
from django.utils.html import format_html

from ...forms import ProgramacionForm
from ...models import Activo, Categoria, DiaHorario, OrdenDeTrabajo, Programacion


from datetime import timedelta




# Función para generar órdenes de trabajo a partir de una programación.
##version que funciona


from datetime import timedelta

from datetime import timedelta

def get_next_day_with_enough_time(hora_actual, duracion_total_pasos, dias_habilitados, dia_map, max_days=365):
    """
    Retorna la hora de inicio del próximo día en el que se disponga de un bloque continuo
    con tiempo suficiente (duracion_total_pasos en minutos) para ejecutar la orden.
    Si no se encuentra un día en el rango de max_days, se lanza un error.
    """
    days_checked = 0
    while days_checked < max_days:
        hora_actual += timedelta(days=1)
        dia = hora_actual.weekday()
        dia_abreviado = dia_map[dia]
        if dia_abreviado in dias_habilitados:
            hora_inicio_dia, hora_final_dia = dias_habilitados[dia_abreviado]
            # Ajusta la hora actual a la hora de inicio del día habilitado
            new_start = hora_actual.replace(hour=hora_inicio_dia.hour, minute=hora_inicio_dia.minute, second=0, microsecond=0)
            new_end = hora_actual.replace(hour=hora_final_dia.hour, minute=hora_final_dia.minute, second=0, microsecond=0)
            available = (new_end - new_start).total_seconds() / 60
            if available >= duracion_total_pasos:
                return new_start
        days_checked += 1
    raise OverflowError("No se encontró un día con suficiente tiempo disponible en un rango de {} días.".format(max_days))


def generar_ordenes(modeladmin, request, queryset):
    # Lista para almacenar todas las órdenes que se van a crear.
    ordenes_creadas = []

    # Iteramos sobre cada programación seleccionada en el admin.
    for programacion in queryset:
        if programacion.programado:
            modeladmin.message_user(
                request,
                f"La programación '{programacion.nombre}' ya fue programada.",
                level='error'
            )
            continue

        hoja_de_ruta = programacion.HojaDeRuta
        horario = programacion.horario if hasattr(programacion, 'horario') else None
        frecuencia = hoja_de_ruta.intervalo if hasattr(hoja_de_ruta, 'intervalo') else None

        if not horario:
            modeladmin.message_user(
                request,
                f"La programación '{programacion.nombre}' no tiene un horario preestablecido asociado.",
                level='error'
            )
            continue

        if not frecuencia:
            modeladmin.message_user(
                request,
                f"La programación '{programacion.nombre}' no tiene una frecuencia asociada.",
                level='error'
            )
            continue

        hora_actual = programacion.fechaDeInicio
        fecha_final = programacion.fecha_final

        duracion_total_pasos = hoja_de_ruta.sumatoria_tiempo_pasos()
        if duracion_total_pasos == 0:
            modeladmin.message_user(
                request,
                f"La programación '{programacion.nombre}' no tiene pasos definidos en la hoja de ruta.",
                level='error'
            )
            continue

        # Se construye un diccionario con los días habilitados y sus horarios.
        dias_habilitados = {
            d.dia: (d.horaInicio, d.horaFinal) for d in programacion.horario.dias_horarios.all()
        }
        # Mapeo para obtener el día abreviado a partir del valor weekday() (0=L, 1=M, ...)
        dia_map = {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V', 5: 'S', 6: 'D'}

        if not dias_habilitados:
            modeladmin.message_user(
                request,
                f"La programación '{programacion.nombre}' no tiene días habilitados en su horario.",
                level='error'
            )
            continue

        # Ciclo principal: se programan órdenes mientras la hora_actual sea menor o igual a la fecha_final.
        while hora_actual <= fecha_final:
            # Guardamos el inicio del ciclo para luego ajustar la fecha con la frecuencia.
            hora_inicio_ciclo = hora_actual
            dia_actual = hora_actual.weekday()
            dia_abreviado_actual = dia_map[dia_actual]

            # Si el día actual no es habilitado, avanzamos al siguiente día.
            if dia_abreviado_actual not in dias_habilitados:
                hora_actual += timedelta(days=1)
                continue

            # Obtenemos el horario del día actual.
            hora_inicio_dia, hora_final_dia = dias_habilitados[dia_abreviado_actual]
            # Ajustamos hora_actual al inicio del bloque disponible del día.
            hora_actual = hora_actual.replace(hour=hora_inicio_dia.hour, minute=hora_inicio_dia.minute, second=0, microsecond=0)
            # Calculamos el final del bloque disponible del día.
            current_day_end = hora_actual.replace(hour=hora_final_dia.hour, minute=hora_final_dia.minute, second=0, microsecond=0)
            available_today = (current_day_end - hora_actual).total_seconds() / 60

            # Procesamos cada área asociada a la programación.
            areas_procesadas = set()
            for area in programacion.areas.all():
                if area in areas_procesadas:
                    continue

                # Verificamos si en el día actual hay tiempo suficiente para la orden completa.
                if available_today < duracion_total_pasos:
                    # Si no hay tiempo suficiente, buscamos el siguiente día que tenga el bloque completo.
                    hora_actual = get_next_day_with_enough_time(hora_actual, duracion_total_pasos, dias_habilitados, dia_map)
                    # Actualizamos los valores del día actual según la nueva fecha.
                    dia_act = hora_actual.weekday()
                    dia_abrev = dia_map[dia_act]
                    hora_inicio_dia, hora_final_dia = dias_habilitados[dia_abrev]
                    current_day_end = hora_actual.replace(hour=hora_final_dia.hour, minute=hora_final_dia.minute, second=0, microsecond=0)
                    available_today = (current_day_end - hora_actual).total_seconds() / 60

                # Ahora que sabemos que hay suficiente tiempo, creamos la orden en un bloque completo.
                try:
                    orden = OrdenDeTrabajo.objects.create(
                        nombre=f"WO-{hoja_de_ruta.nombre} - {area.nombre}",
                        HojaDeRuta=hoja_de_ruta,
                        horario=horario,
                        fechaDeInicio=hora_actual,
                        fechaDeFin=hora_actual + timedelta(minutes=duracion_total_pasos),
                        area=area,
                        programacion=programacion
                    )
                    ordenes_creadas.append(orden)
                except Exception as e:
                    modeladmin.message_user(
                        request,
                        f"Error al crear orden para '{area.nombre}': {str(e)}",
                        level='error'
                    )
                    continue

                # Actualizamos hora_actual al finalizar la orden y recalculamos el tiempo disponible.
                hora_actual += timedelta(minutes=duracion_total_pasos)
                available_today = (current_day_end - hora_actual).total_seconds() / 60
                areas_procesadas.add(area)

            # Luego de procesar todas las áreas en este ciclo, avanzamos la hora_actual según la FRECUENCIA.
            hora_actual = hora_inicio_ciclo + timedelta(days=frecuencia.intervalo)

        # Se marca la programación como completada.
        programacion.programado = True
        programacion.save()

    modeladmin.message_user(request, f"Órdenes generadas: {len(ordenes_creadas)}")


# Se define la descripción corta para la acción en el admin.
generar_ordenes.short_description = "Generar órdenes de trabajo"


from datetime import timedelta

#Funcion para generar órdenes de trabajo a partir de una programación por activo

from datetime import timedelta

def generar_ordenes_por_activo(modeladmin, request, queryset):
    ordenes_creadas = []

    for programacion in queryset:
        print(f"Procesando programación: {programacion.nombre}")
        
        if programacion.programado:
            modeladmin.message_user(
                request, 
                f"La programación '{programacion.nombre}' ya fue programada.", 
                level='error'
            )
            continue

        hoja_de_ruta = programacion.HojaDeRuta
        print(f"Hoja de ruta: {hoja_de_ruta.nombre}")
        
        # Obtener el horario de una relación separada de la programación
        horario = programacion.horario  # Asumiendo que hay una relación directa con horario
        frecuencia = hoja_de_ruta.intervalo if hasattr(hoja_de_ruta, 'intervalo') else None

        if not horario:
            modeladmin.message_user(
                request, 
                f"La programación '{programacion.nombre}' no tiene un horario preestablecido asociado.", 
                level='error'
            )
            continue
        
        if not frecuencia:
            modeladmin.message_user(
                request, 
                f"La programación '{programacion.nombre}' no tiene una frecuencia asociada.", 
                level='error'
            )
            continue

        print(f"Horario: {horario}, Frecuencia: {frecuencia}")

        hora_actual = programacion.fechaDeInicio
        fecha_final = programacion.fecha_final

        print(f"Fecha de inicio: {hora_actual}, Fecha final: {fecha_final}")

        duracion_total_pasos = hoja_de_ruta.sumatoria_tiempo_pasos()
        if duracion_total_pasos == 0:
            modeladmin.message_user(
                request, 
                f"La programación '{programacion.nombre}' no tiene pasos definidos en la hoja de ruta.", 
                level='error'
            )
            continue

        print(f"Duración total de pasos: {duracion_total_pasos} minutos")

        dias_habilitados = {d.dia: (d.horaInicio, d.horaFinal) for d in horario.dias_horarios.all()}
        dia_map = {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V', 5: 'S', 6: 'D'}

        while hora_actual <= fecha_final:
            dia_actual = hora_actual.weekday()
            dia_abreviado_actual = dia_map[dia_actual]

            print(f"Día actual: {dia_abreviado_actual}")

            if dia_abreviado_actual not in dias_habilitados:
                hora_actual += timedelta(days=1)
                continue

            hora_inicio, hora_final = dias_habilitados[dia_abreviado_actual]
            hora_actual = hora_actual.replace(hour=hora_inicio.hour, minute=hora_inicio.minute)

            activos_procesados = set()

            for activo in programacion.activos.all():
                print(f"Procesando activo: {activo.no_inventario}")

                # Creamos una orden por activo
                tiempo_restante = duracion_total_pasos

                while tiempo_restante > 0:
                    hora_fin_horario = hora_actual.replace(hour=hora_final.hour, minute=hora_final.minute)
                    tiempo_disponible = max(0, (hora_fin_horario - hora_actual).total_seconds() / 60)

                    print(f"Tiempo disponible: {tiempo_disponible} minutos")

                    if tiempo_disponible == 0:
                        while True:
                            hora_actual += timedelta(days=1)
                            dia_actual = hora_actual.weekday()
                            dia_abreviado_actual = dia_map[dia_actual]
                            if dia_abreviado_actual in dias_habilitados:
                                hora_inicio, _ = dias_habilitados[dia_abreviado_actual]
                                hora_actual = hora_actual.replace(hour=hora_inicio.hour, minute=hora_inicio.minute)
                                break
                        continue

                    duracion_parte = min(tiempo_restante, tiempo_disponible)

                    if duracion_parte > 0:
                        # Crear una orden de trabajo para el activo
                        orden = OrdenDeTrabajo.objects.create(
                            nombre=f"WO-{hoja_de_ruta.nombre} - {activo.no_inventario}",
                            HojaDeRuta=hoja_de_ruta,
                            fechaDeInicio=hora_actual,
                            fechaDeFin=hora_actual + timedelta(minutes=duracion_parte),
                            Activo=activo,  # Asociamos el activo a la orden de trabajo
                            # También asociamos el área si es necesario
                        )
                        ordenes_creadas.append(orden)

                        print(f"Orden de trabajo creada: {orden.nombre}")

                    tiempo_restante -= duracion_parte
                    hora_actual += timedelta(minutes=duracion_parte)

                    if tiempo_restante > 0:
                        while True:
                            hora_actual += timedelta(days=1)
                            dia_actual = hora_actual.weekday()
                            dia_abreviado_actual = dia_map[dia_actual]
                            if dia_abreviado_actual in dias_habilitados:
                                hora_inicio, _ = dias_habilitados[dia_abreviado_actual]
                                hora_actual = hora_actual.replace(hour=hora_inicio.hour, minute=hora_inicio.minute)
                                break

            hora_actual += timedelta(days=frecuencia.intervalo)

        programacion.programado = True
        programacion.save()

    modeladmin.message_user(request, f"Órdenes generadas: {len(ordenes_creadas)}")
    print(f"Total de órdenes generadas: {len(ordenes_creadas)}")

generar_ordenes_por_activo.short_description = "Generar órdenes de trabajo por activo"

def eliminar_ordenes(modeladmin, request, queryset):
    ordenes_eliminadas = []
    for programacion in queryset:
        ordenes = OrdenDeTrabajo.objects.filter(programacion=programacion)
        count = ordenes.count()
        ordenes.delete()
        ordenes_eliminadas.append(f"{programacion.nombre} ({count} órdenes eliminadas)")
    
    modeladmin.message_user(request, f"Órdenes eliminadas: {', '.join(ordenes_eliminadas)}")

eliminar_ordenes.short_description = "Eliminar órdenes de trabajo"

class ActivoInline(admin.TabularInline):  
    model = Programacion.activos.through  # Relación ManyToMany intermedia
    extra = 1  
    verbose_name = "Activo"
    verbose_name_plural = "Activos"

    def get_readonly_fields(self, request, obj=None):
        return ['activo_nombre']  # Solo lectura

    def activo_nombre(self, instance):
        return instance.activo.nombre  # Muestra el nombre del activo

    activo_nombre.short_description = "Nombre del Activo"




@admin.register(Programacion)
class ProgramacionAdmin(admin.ModelAdmin):
    form = ProgramacionForm
    list_display = ('nombre', 'fechaDeInicio', 'programado','horario')
    list_editable = ('fechaDeInicio','programado','horario')
    list_filter = ('programado', 'fechaDeInicio', 'activos__modelo__categoria')  # ✅ Filtro correcto
    actions = [generar_ordenes, generar_ordenes_por_activo, eliminar_ordenes]
    search_fields = ('nombre', 'fechaDeInicio')
    
    # Agregar filtro horizontal para activos
    filter_horizontal = ('activos',)
    