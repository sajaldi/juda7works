import openpyxl
from openpyxl.styles import Font
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd
from cmms.models import Herramienta, Unidad, Marca, Categoria  # Importa tus modelos
import datetime

def exportar_plantilla_herramientas(request):
    """
    Exporta la plantilla de herramientas en formato Excel.
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Herramientas"

    headers = ['ID', 'Nombre', 'Descripción', 'Unidad', 'Marca', 'Categorías']
    sheet.append(headers)

    # Estilo para encabezados
    bold_font = Font(bold=True)
    for cell in sheet[1]:
        cell.font = bold_font

    # Obtener todas las herramientas (optimizado)
    herramientas = Herramienta.objects.all().select_related('unidad', 'marca').prefetch_related('categoria')

    for herramienta in herramientas:
        categorias_str = ", ".join(cat.nombre for cat in herramienta.categoria.all())  # Más eficiente
        sheet.append([
            herramienta.id,
            herramienta.nombre,
            herramienta.descripcion or "",
            herramienta.unidad.nombre if herramienta.unidad else "",
            herramienta.marca.nombre if herramienta.marca else "",
            categorias_str
        ])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename="plantilla_herramientas_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx"'

    return response

def importar_herramientas_view(request):
    """
    Vista para importar herramientas desde un archivo Excel o CSV.
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
            columnas_requeridas = ['id', 'nombre', 'descripción', 'unidad', 'marca', 'categorías']

            if not all(col in df.columns for col in columnas_requeridas):
                messages.error(request, "Faltan columnas. Use la plantilla.")
                return redirect(request.path)

            errores = []
            for index, row in df.iterrows():
                herramienta_id = row['id']
                nombre = row['nombre']
                descripcion = row['descripción']
                unidad_nombre = row['unidad']
                marca_nombre = row['marca']
                categorias_nombres = [cat.strip() for cat in row['categorías'].split(',')] if row['categorías'] else []

                # Validación (simplificada)
                if not all([nombre, descripcion, unidad_nombre, marca_nombre]):
                    errores.append(f"Fila {index + 2}: Datos obligatorios incompletos.")
                    continue

                try:
                    unidad, _ = Unidad.objects.get_or_create(nombre=unidad_nombre)
                    marca, _ = Marca.objects.get_or_create(nombre=marca_nombre)
                    
                    herramienta, created = Herramienta.objects.update_or_create(
                        id=herramienta_id,
                        defaults={
                            'nombre': nombre,
                            'descripcion': descripcion,
                            'unidad': unidad,
                            'marca': marca,
                        }
                    )

                    # Actualización de categorías (más eficiente)
                    herramienta.categoria.set([Categoria.objects.get_or_create(nombre=cat)[0] for cat in categorias_nombres])

                    if created:
                        print(f"Fila {index + 2}: Herramienta creada.")
                    else:
                        print(f"Fila {index + 2}: Herramienta actualizada.")

                except Exception as e:
                    errores.append(f"Fila {index + 2}: Error: {e}")

            if errores:
                messages.error(request, "Errores en la importación:\n" + "\n".join(errores))
            else:
                messages.success(request, "Importación exitosa.")

        except Exception as e:
            messages.error(request, f"Error al procesar archivo: {e}")

        return redirect(request.path)

    return render(request, "cmms/importar_herramientas.html")  # Asegúrate de tener la plantilla