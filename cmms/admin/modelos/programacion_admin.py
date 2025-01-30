from datetime import datetime, timedelta
from django.contrib import admin
from django.shortcuts import render

from ...models import DiaHorario, OrdenDeTrabajo, Programacion


from datetime import timedelta

from datetime import timedelta

from datetime import timedelta

from datetime import timedelta


from datetime import timedelta

def generar_ordenes(modeladmin, request, queryset):
    ordenes_creadas = []

    for programacion in queryset:
        if programacion.programado:
            modeladmin.message_user(request, f"La programación '{programacion.nombre}' ya fue programada.", level='error')
            continue

        hoja_de_ruta = programacion.HojaDeRuta
        horario = hoja_de_ruta.horario if hasattr(hoja_de_ruta, 'horario') else None
        frecuencia = hoja_de_ruta.intervalo if hasattr(hoja_de_ruta, 'intervalo') else None

        if not horario:
            modeladmin.message_user(request, f"La programación '{programacion.nombre}' no tiene un horario preestablecido asociado.", level='error')
            continue
        if not frecuencia:
            modeladmin.message_user(request, f"La programación '{programacion.nombre}' no tiene una frecuencia asociada.", level='error')
            continue

        hora_actual = programacion.fechaDeInicio
        fecha_final = programacion.fecha_final
        duracion_total_pasos = hoja_de_ruta.sumatoria_tiempo_pasos()

        if duracion_total_pasos == 0:
            modeladmin.message_user(request, f"La programación '{programacion.nombre}' no tiene pasos definidos en la hoja de ruta.", level='error')
            continue

        # Obtener los días habilitados desde la relación con DiaHorario
        dias_habilitados = {d.dia: (d.horaInicio, d.horaFinal) for d in horario.dias_horarios.all()}

        # Mapeo de días
        dia_map = {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V', 5: 'S', 6: 'D'}

        while hora_actual <= fecha_final:
            dia_actual = hora_actual.weekday()
            dia_abreviado_actual = dia_map[dia_actual]

            if dia_abreviado_actual not in dias_habilitados:
                hora_actual += timedelta(days=1)
                continue

            hora_inicio, hora_final = dias_habilitados[dia_abreviado_actual]
            # Reiniciar al inicio del horario si el ciclo se repite
            hora_actual = hora_actual.replace(hour=hora_inicio.hour, minute=hora_inicio.minute)

            for area in programacion.areas.all():  # Asegurar que se genera una orden por cada área
                tiempo_restante = duracion_total_pasos

                while tiempo_restante > 0:
                    hora_fin_horario = hora_actual.replace(hour=hora_final.hour, minute=hora_final.minute)
                    tiempo_disponible = max(0, (hora_fin_horario - hora_actual).total_seconds() / 60)

                    if tiempo_disponible == 0:
                        # Si el tiempo disponible es 0, saltamos al siguiente día hábil
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

                    # Verificamos que la orden tenga una duración válida
                    if duracion_parte > 0:
                        orden = OrdenDeTrabajo.objects.create(
                            nombre=f"WO-{hoja_de_ruta.nombre} - {area.nombre}",
                            HojaDeRuta=hoja_de_ruta,
                            fechaDeInicio=hora_actual,
                            fechaDeFin=hora_actual + timedelta(minutes=duracion_parte),
                            area=area
                        )
                        ordenes_creadas.append(orden)

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



generar_ordenes.short_description = "Generar órdenes de trabajo"



def eliminar_ordenes(modeladmin, request, queryset):
    ordenes_eliminadas = []
    for programacion in queryset:
        ordenes = OrdenDeTrabajo.objects.filter(programacion=programacion)
        count = ordenes.count()
        ordenes.delete()
        ordenes_eliminadas.append(f"{programacion.nombre} ({count} órdenes eliminadas)")
    
    modeladmin.message_user(request, f"Órdenes eliminadas: {', '.join(ordenes_eliminadas)}")

eliminar_ordenes.short_description = "Eliminar órdenes de trabajo"

@admin.register(Programacion)
class ProgramacionAdmin(admin.ModelAdmin):
    list_display=('nombre',)
    autocomplete_fields = ['activos']  # Campo relacionado a Activo con búsqueda y paginación
    actions = [generar_ordenes, eliminar_ordenes]
    
   