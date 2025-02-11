import openpyxl
from openpyxl.styles import Font
from io import BytesIO
import datetime
import pandas as pd
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from cmms.models import Puesto, HorarioPreestablecido

def gestionar_puestos(request):
    """
    Vista para gestionar la exportación e importación de puestos de trabajo.
    """
    if request.method == "POST" and request.FILES.get("archivo"):
        # Lógica de importación
        archivo = request.FILES["archivo"]
        extension = archivo.name.split('.')[-1].lower()

        if extension not in ["csv", "xlsx", "xls"]:
            messages.error(request, "Formato no soportado. Debe ser CSV o Excel.")
            return redirect(request.path)

        try:
            if extension == "csv":
                df = pd.read_csv(archivo, dtype=str, keep_default_na=False)
            else:
                df = pd.read_excel(archivo, dtype=str, keep_default_na=False)

            df.columns = [col.strip().lower() for col in df.columns]
            columnas_requeridas = ['id', 'nombre', 'descripción', 'horario preestablecido']

            if not all(col in df.columns for col in columnas_requeridas):
                messages.error(request, "Faltan columnas. Use la plantilla.")
                return redirect(request.path)

            errores = []
            for index, row in df.iterrows():
                puesto_id = row['id']
                nombre = row['nombre']
                descripcion = row['descripción']
                horario_nombre = row['horario preestablecido']

                # Validación (simplificada)
                if not all([nombre, descripcion, horario_nombre]):
                    errores.append(f"Fila {index + 2}: Datos obligatorios incompletos.")
                    continue

                try:
                    horario, _ = HorarioPreestablecido.objects.get_or_create(nombre=horario_nombre)
                    
                    puesto, created = Puesto.objects.update_or_create(
                        id=puesto_id,
                        defaults={
                            'nombre': nombre,
                            'descripcion': descripcion,
                            'HorarioPreestablecido': horario,
                        }
                    )

                    if created:
                        print(f"Fila {index + 2}: Puesto de trabajo creado.")
                    else:
                        print(f"Fila {index + 2}: Puesto de trabajo actualizado.")

                except Exception as e:
                    errores.append(f"Fila {index + 2}: Error: {e}")

            if errores:
                messages.error(request, "Errores en la importación:\n" + "\n".join(errores))
            else:
                messages.success(request, "Importación exitosa.")

        except Exception as e:
            messages.error(request, f"Error al procesar archivo: {e}")

        return redirect(request.path)

    elif request.method == "GET" and "exportar" in request.GET:
        # Lógica de exportación
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Puestos de Trabajo"

        headers = ['ID', 'Nombre', 'Descripción', 'Horario Preestablecido']
        sheet.append(headers)

        # Estilo para encabezados
        bold_font = Font(bold=True)
        for cell in sheet[1]:
            cell.font = bold_font

        # Obtener todos los puestos de trabajo
        puestos = Puesto.objects.all().select_related('HorarioPreestablecido')

        for puesto in puestos:
            sheet.append([
                puesto.id,
                puesto.nombre,
                puesto.descripcion or "",
                puesto.HorarioPreestablecido.nombre if puesto.HorarioPreestablecido else ""
            ])

        output = BytesIO()
        workbook.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = f'attachment; filename="plantilla_puestos_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx"'

        return response

    return render(request, "cmms/gestionar_puestos.html")  # Asegúrate de tener la plantilla
