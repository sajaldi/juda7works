import pandas as pd
import openpyxl
from openpyxl.styles import Font
from io import BytesIO
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from cmms.models import Sistema
import datetime

def importar_sistemas_view(request):
    """
    Vista para importar sistemas desde un archivo Excel o CSV.
    """
    if request.method == "POST" and request.FILES.get("archivo"):
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
            columnas_requeridas = ['id', 'nombre', 'principal']  # Asegúrate de que la columna ID esté presente

            if not all(col in df.columns for col in columnas_requeridas):
                messages.error(request, "Faltan columnas. Use la plantilla.")
                return redirect(request.path)

            errores = []
            for index, row in df.iterrows():
                sistema_id = row['id']
                nombre = row['nombre']
                principal_nombre = row['principal']

                # Validación (simplificada)
                if not nombre:
                    errores.append(f"Fila {index + 2}: Nombre obligatorio.")
                    continue

                try:
                    if principal_nombre:
                        principal = Sistema.objects.get(nombre=principal_nombre)
                    else:
                        principal = None

                    # Actualizar o crear el sistema por ID
                    Sistema.objects.update_or_create(
                        id=sistema_id,  # Usamos el ID para buscar o crear
                        defaults={'nombre': nombre, 'principal': principal}
                    )

                except Sistema.DoesNotExist:
                    errores.append(f"Fila {index + 2}: Sistema principal '{principal_nombre}' no encontrado.")
                except Exception as e:
                    errores.append(f"Fila {index + 2}: Error: {e}")

            if errores:
                messages.error(request, "Errores en la importación:\n" + "\n".join(errores))
            else:
                messages.success(request, "Importación exitosa.")

        except Exception as e:
            messages.error(request, f"Error al procesar archivo: {e}")

        return redirect(request.path)

    return render(request, "cmms/importar_sistemas.html")  # Asegúrate de tener la plantilla


def exportar_plantilla_sistemas(request):
    """
    Exporta la plantilla de sistemas en formato Excel, incluyendo el ID.
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Sistemas"

    headers = ['ID', 'Nombre', 'Principal']
    sheet.append(headers)

    bold_font = Font(bold=True)
    for cell in sheet[1]:
        cell.font = bold_font

    sistemas = Sistema.objects.all().select_related('principal')

    for sistema in sistemas:
        principal_nombre = sistema.principal.nombre if sistema.principal else ""
        sheet.append([
            sistema.id,  # Incluye el ID
            sistema.nombre,
            principal_nombre
        ])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename="plantilla_sistemas_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx"'

    return response
