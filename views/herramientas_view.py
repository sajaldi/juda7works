

import datetime
from pyexpat.errors import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
import openpyxl
import pandas as pd

from cmms.models import Categoria, Herramienta, Marca, Unidad


def exportar_plantilla_herramientas(request):
    """
    Exporta la plantilla de herramientas en formato Excel.
    """
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Herramientas"

    headers = ['Nombre', 'Descripción', 'Unidad', 'Marca', 'Categorías']  # Incluye categorías
    sheet.append(headers)

    herramientas = Herramienta.objects.all()
    for herramienta in herramientas:
        categorias_str = ", ".join([cat.nombre for cat in herramienta.categoria.all()])  # Formatea categorías como string
        sheet.append([
            herramienta.nombre,
            herramienta.descripcion,
            herramienta.unidad.nombre if herramienta.unidad else "",
            herramienta.marca.nombre if herramienta.marca else "",
            categorias_str  # Añade la cadena de categorías
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="plantilla_herramientas_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx"'

    workbook.save(response)
    return response


def importar_herramientas_view(request):
    """
    Vista para importar herramientas desde un archivo Excel o CSV.
    """
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]
        extension = archivo.name.split('.')[-1].lower()

        if extension not in ["csv", "xlsx", "xls"]:
            messages.error(request, "Formato no soportado. Por favor, suba un archivo CSV o Excel (.xlsx, .xls).")
            return redirect(request.path)

        try:
            if extension == "csv":
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)

            columnas_requeridas = ['Nombre', 'Descripción', 'Unidad', 'Marca', 'Categorías']  # Incluye categorías
            if not all(col in df.columns for col in columnas_requeridas):
                messages.error(request, "El archivo no tiene las columnas correctas. Use la plantilla de importación.")
                return redirect(request.path)

            for _, row in df.iterrows():
                unidad, _ = Unidad.objects.get_or_create(nombre=row['Unidad'].strip()) if pd.notna(row['Unidad']) else (None, None)
                marca, _ = Marca.objects.get_or_create(nombre=row['Marca'].strip()) if pd.notna(row['Marca']) else (None, None)

                # Manejo de categorías (separadas por comas en el archivo)
                categorias_nombres = [cat.strip() for cat in row['Categorías'].split(',')] if pd.notna(row['Categorías']) else []
                categorias = []
                for cat_nombre in categorias_nombres:
                    categoria, _ = Categoria.objects.get_or_create(nombre=cat_nombre)
                    categorias.append(categoria)


                herramienta, _ = Herramienta.objects.update_or_create(
                    nombre=row['Nombre'], # Usar nombre como identificador único
                    defaults={
                        'descripcion': row['Descripción'],
                        'unidad': unidad,
                        'marca': marca,
                        # Las categorías se añaden después de crear/actualizar la herramienta
                    }
                )
                herramienta.categoria.set(categorias) # Asigna las categorías a la herramienta


            messages.success(request, "Herramientas importadas correctamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")

        return redirect(request.path)

    return render(request, "cmms/importar_herramientas.html")  # Asegúrate de tener el template correcto