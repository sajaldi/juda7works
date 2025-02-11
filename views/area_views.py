from django.shortcuts import redirect, render
import openpyxl
from openpyxl.styles import Font
from io import BytesIO
from django.http import HttpResponse
import datetime
import pandas as pd
from django.contrib import messages
from cmms.models import Area


def exportar_plantilla_areas(request):
    """
    Exporta la plantilla de áreas en formato Excel.
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Areas"

    headers = ['ID', 'Nombre', 'Área Principal', 'Identificador']
    sheet.append(headers)

    # Estilo para encabezados
    bold_font = Font(bold=True)
    for cell in sheet[1]:
        cell.font = bold_font

    # Obtener todas las áreas (optimizado)
    areas = Area.objects.all().select_related('principal')

    for area in areas:
        sheet.append([
            area.id,
            area.nombre,
            area.principal.nombre if area.principal else "",
            area.identificador or ""
        ])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename="plantilla_areas_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx"'

    return response

def importar_areas_view(request):
    """
    Vista para importar áreas desde un archivo Excel o CSV.
    """
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]
        extension = archivo.name.split('.')[-1].lower()

        if extension not in ["csv", "xlsx", "xls"]:
            messages.error(request, "Formato no soportado. Debe ser CSV o Excel.")
            return redirect(request.path)

        try:
            if extension == "csv":
                df = pd.read_csv(archivo, dtype=str, keep_default_na=False)  # Manejar celdas vacías
            else:
                df = pd.read_excel(archivo, dtype=str, keep_default_na=False)

            df.columns = [col.strip().lower() for col in df.columns]
            columnas_requeridas = ['id', 'nombre', 'área principal', 'identificador']

            if not all(col in df.columns for col in columnas_requeridas):
                messages.error(request, "Faltan columnas. Use la plantilla.")
                return redirect(request.path)

            errores = []
            for index, row in df.iterrows():
                area_id = row['id']
                nombre = row['nombre']
                area_principal_nombre = row['área principal']
                identificador = row['identificador']

                # Validación (simplificada)
                if not nombre:
                    errores.append(f"Fila {index + 2}: Nombre es obligatorio.")
                    continue

                try:
                    area_principal = Area.objects.get(nombre=area_principal_nombre) if area_principal_nombre else None

                    area, created = Area.objects.update_or_create(
                        id=area_id,
                        defaults={
                            'nombre': nombre,
                            'principal': area_principal,
                            'identificador': identificador
                        }
                    )

                    if created:
                        print(f"Fila {index + 2}: Área creada.")
                    else:
                        print(f"Fila {index + 2}: Área actualizada.")

                except Exception as e:
                    errores.append(f"Fila {index + 2}: Error: {e}")

            if errores:
                messages.error(request, "Errores en la importación:\n" + "\n".join(errores))
            else:
                messages.success(request, "Importación exitosa.")

        except Exception as e:
            messages.error(request, f"Error al procesar archivo: {e}")

        return redirect(request.path)

    return render(request, "cmms/importar_areas.html")  # Asegúrate de tener la plantilla