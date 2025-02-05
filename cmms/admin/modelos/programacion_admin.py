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
def generar_ordenes(modeladmin, request, queryset):
    # Lista para almacenar todas las órdenes que se van a crear.
    ordenes_creadas = []

    # Iteramos sobre cada programación seleccionada en el admin.
    for programacion in queryset:
        # Si la programación ya fue procesada (programado=True), se omite.
        if programacion.programado:
            modeladmin.message_user(
                request, 
                f"La programación '{programacion.nombre}' ya fue programada.", 
                level='error'
            )
            continue

        # Se obtiene la hoja de ruta asociada a la programación.
        hoja_de_ruta = programacion.HojaDeRuta
        
        # Se obtiene el horario preestablecido de la hoja de ruta (si existe).
        horario = hoja_de_ruta.horario if hasattr(hoja_de_ruta, 'horario') else None
        
        # Se obtiene la frecuencia (intervalo) de la hoja de ruta (si existe).
        frecuencia = hoja_de_ruta.intervalo if hasattr(hoja_de_ruta, 'intervalo') else None

        # Si no hay horario, se muestra un mensaje de error y se continúa con la siguiente programación.
        if not horario:
            modeladmin.message_user(
                request, 
                f"La programación '{programacion.nombre}' no tiene un horario preestablecido asociado.", 
                level='error'
            )
            continue
        
        # Si no hay frecuencia, se muestra un mensaje de error y se continúa.
        if not frecuencia:
            modeladmin.message_user(
                request, 
                f"La programación '{programacion.nombre}' no tiene una frecuencia asociada.", 
                level='error'
            )
            continue

        # Se inicializa la hora_actual con la fecha de inicio de la programación.
        hora_actual = programacion.fechaDeInicio
        # Se obtiene la fecha final de la programación.
        fecha_final = programacion.fecha_final

        # Se obtiene la duración total (en minutos) de los pasos de la hoja de ruta.
        duracion_total_pasos = hoja_de_ruta.sumatoria_tiempo_pasos()
        if duracion_total_pasos == 0:
            modeladmin.message_user(
                request, 
                f"La programación '{programacion.nombre}' no tiene pasos definidos en la hoja de ruta.", 
                level='error'
            )
            continue

        # Se construye un diccionario con los días habilitados.
        # Cada clave es la abreviatura del día (ejemplo 'L' para lunes) y el valor es una tupla (horaInicio, horaFinal)
        # obtenida de los objetos de la relación DiaHorario.
        dias_habilitados = {d.dia: (d.horaInicio, d.horaFinal) for d in horario.dias_horarios.all()}

        # Mapeo de los números de día (weekday) a abreviaturas:
        # 0: Lunes ('L'), 1: Martes ('M'), 2: Miércoles ('X'), 3: Jueves ('J'),
        # 4: Viernes ('V'), 5: Sábado ('S'), 6: Domingo ('D')
        dia_map = {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V', 5: 'S', 6: 'D'}

        # Se inicia un ciclo while para generar órdenes mientras la hora_actual sea menor o igual a la fecha final.
        while hora_actual <= fecha_final:
            # Se obtiene el día de la semana de la hora_actual (número 0 a 6)
            dia_actual = hora_actual.weekday()
            # Se mapea el número del día a su abreviatura correspondiente.
            dia_abreviado_actual = dia_map[dia_actual]

            # Si el día actual (abreviado) no está en los días habilitados, se incrementa la hora_actual un día y se continúa.
            if dia_abreviado_actual not in dias_habilitados:
                hora_actual += timedelta(days=1)
                continue

            # Se obtienen el horario de inicio y fin para el día actual, según la configuración.
            hora_inicio, hora_final = dias_habilitados[dia_abreviado_actual]
            # Se ajusta la hora_actual para que comience en la hora de inicio definida.
            hora_actual = hora_actual.replace(hour=hora_inicio.hour, minute=hora_inicio.minute)

            # Se crea un conjunto para llevar un seguimiento de las áreas (niveles) ya procesadas en este ciclo.
            areas_procesadas = set()

            # Se itera sobre cada área asociada a la programación.
            for area in programacion.areas.all():
                # Si el área ya fue procesada, se omite.
                if area in areas_procesadas:
                    continue

                # Inicialmente, el tiempo_restante es la duración total de los pasos de la hoja de ruta.
                tiempo_restante = duracion_total_pasos

                # Se procesa la orden mientras quede tiempo pendiente.
                while tiempo_restante > 0:
                    # Se calcula el final del horario del día actual ajustando la hora_actual a la hora final de la jornada.
                    hora_fin_horario = hora_actual.replace(hour=hora_final.hour, minute=hora_final.minute)
                    # Se calcula el tiempo disponible en minutos desde la hora_actual hasta el final de la jornada.
                    tiempo_disponible = max(0, (hora_fin_horario - hora_actual).total_seconds() / 60)

                    # Si no hay tiempo disponible en la jornada actual, se busca el siguiente día habilitado:
                    if tiempo_disponible == 0:
                        while True:
                            # Se incrementa la hora_actual un día.
                            hora_actual += timedelta(days=1)
                            # Se actualiza el día y su abreviatura.
                            dia_actual = hora_actual.weekday()
                            dia_abreviado_actual = dia_map[dia_actual]
                            # Si el nuevo día es habilitado, se ajusta la hora_actual al inicio de la jornada de ese día.
                            if dia_abreviado_actual in dias_habilitados:
                                hora_inicio, _ = dias_habilitados[dia_abreviado_actual]
                                hora_actual = hora_actual.replace(hour=hora_inicio.hour, minute=hora_inicio.minute)
                                break
                        continue

                    # Se calcula la duración de la parte de la orden que se puede programar en el día actual.
                    # Es el mínimo entre el tiempo pendiente y el tiempo disponible.
                    duracion_parte = min(tiempo_restante, tiempo_disponible)

                    # Si se puede programar una parte (duracion_parte > 0), se crea la orden de trabajo.
                    if duracion_parte > 0:
                        orden = OrdenDeTrabajo.objects.create(
                            nombre=f"WO-{hoja_de_ruta.nombre} - {area.nombre}",
                            HojaDeRuta=hoja_de_ruta,
                            fechaDeInicio=hora_actual,
                            fechaDeFin=hora_actual + timedelta(minutes=duracion_parte),
                            area=area
                        )
                        # Se agrega la orden creada a la lista.
                        ordenes_creadas.append(orden)

                    # Se reduce el tiempo_restante con la duración de la parte programada.
                    tiempo_restante -= duracion_parte
                    # Se actualiza la hora_actual sumándole la duración de la parte creada.
                    hora_actual += timedelta(minutes=duracion_parte)

                    # Si todavía queda tiempo pendiente para completar la rutina,
                    # se busca el siguiente día habilitado para continuar.
                    if tiempo_restante > 0:
                        while True:
                            hora_actual += timedelta(days=1)
                            dia_actual = hora_actual.weekday()
                            dia_abreviado_actual = dia_map[dia_actual]
                            if dia_abreviado_actual in dias_habilitados:
                                hora_inicio, _ = dias_habilitados[dia_abreviado_actual]
                                hora_actual = hora_actual.replace(hour=hora_inicio.hour, minute=hora_inicio.minute)
                                break

                # Una vez completada la orden para el área, se marca el área como procesada.
                areas_procesadas.add(area)

            # Al finalizar el procesamiento de todas las áreas en el día, se incrementa la hora_actual 
            # sumándole el intervalo definido en la frecuencia (en días) para la siguiente iteración.
            hora_actual += timedelta(days=frecuencia.intervalo)

        # Se marca la programación como programada y se guarda.
        programacion.programado = True
        programacion.save()

    # Se notifica en el admin cuántas órdenes se han generado.
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
        
        horario = hoja_de_ruta.horario if hasattr(hoja_de_ruta, 'horario') else None
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
    list_display = ('nombre', 'fechaDeInicio', 'programado')
    list_editable = ('fechaDeInicio',)
    list_filter = ('programado', 'fechaDeInicio', 'activos__modelo__categoria')  # ✅ Filtro correcto
    actions = [generar_ordenes, generar_ordenes_por_activo, eliminar_ordenes]
    search_fields = ('nombre', 'fechaDeInicio')
    
    # Agregar filtro horizontal para activos
    filter_horizontal = ('activos',)
    