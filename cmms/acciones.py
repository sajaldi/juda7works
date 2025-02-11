import csv
import datetime
import io
import openpyxl
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd
from .models import Activo, Herramienta, Marca, Modelo, Categoria, PasosHojaDeRuta, Unidad



def exportar_plantilla_activos(request):
    """
    Exporta la plantilla de activos en formato Excel con los datos actuales de la base de datos.
    """
    # Crear un nuevo archivo de Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Activos"

    # Escribir la cabecera del archivo
    headers = ['ID', 'Nombre', 'Marca', 'No. Inventario', 'Modelo']
    sheet.append(headers)

    # Obtener y escribir los datos existentes
    activos = Activo.objects.all()
    for activo in activos:
        sheet.append([
            activo.id,
            activo.nombre,
            activo.marca.nombre if activo.marca else "",
            activo.no_inventario,
            activo.modelo.nombre if activo.modelo else ""
        ])

    # Configurar la respuesta HTTP como archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="plantilla_activos_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx"'

    # Guardar el archivo Excel en la respuesta
    workbook.save(response)
    return response


def importar_activos_view(request):
    """
    Vista para importar activos desde un archivo Excel o CSV.
    """
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]
        extension = archivo.name.split('.')[-1].lower()

        # Validar formato de archivo
        if extension not in ["csv", "xlsx", "xls"]:
            messages.error(request, "Formato no soportado. Por favor, suba un archivo CSV o Excel (.xlsx, .xls).")
            return redirect(request.path)

        try:
            # Leer archivo según el formato
            if extension == "csv":
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)

            # Validar que el archivo tenga las columnas necesarias
            columnas_requeridas = ['ID', 'Nombre', 'Marca', 'No. Inventario', 'Modelo']
            if not all(col in df.columns for col in columnas_requeridas):
                messages.error(request, "El archivo no tiene las columnas correctas. Use la plantilla de importación.")
                return redirect(request.path)

            # Procesar cada fila del archivo
            for _, row in df.iterrows():
                # Obtener o crear Marca y Modelo
                marca, _ = Marca.objects.get_or_create(nombre=row['Marca'].strip()) if pd.notna(row['Marca']) else (None, None)
                modelo, _ = Modelo.objects.get_or_create(nombre=row['Modelo'].strip()) if pd.notna(row['Modelo']) else (None, None)

                # Crear o actualizar Activo
                Activo.objects.update_or_create(
                    id=row['ID'],
                    defaults={
                        'nombre': row['Nombre'],
                        'marca': marca,
                        'no_inventario': row['No. Inventario'],
                        'modelo': modelo
                    }
                )

            messages.success(request, "Activos importados correctamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")

        return redirect(request.path)

    return render(request, "admin/importar_activos.html")



def exportar_plantilla_pasos(request):
    """
    Exporta la plantilla de activos en formato Excel con los datos actuales de la base de datos.
    """
    # Crear un nuevo archivo de Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Pasos"

    # Escribir la cabecera del archivo
    headers = ['Paso', 'HojaDeRuta',]
    sheet.append(headers)

    #class PasosHojaDeRuta(models.Model):
    #paso = models.CharField(max_length=100)
    #tiempo = models.IntegerField(null=True)
    #hojaderuta = models.ForeignKey(HojaDeRuta, on_delete=models.CASCADE)

    # Obtener y escribir los datos existentes
    pasos = PasosHojaDeRuta.objects.all()
    for paso in pasos:
        sheet.append([
            pasos.paso,
            pasos.hojaderuta.nombre if pasos.hojaderuta else "",        ])

    # Configurar la respuesta HTTP como archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="plantilla_activos_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx"'

    # Guardar el archivo Excel en la respuesta
    workbook.save(response)
    return response


def importar_pasos_view(request):
    """
    Vista para importar activos desde un archivo Excel o CSV.
    """
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]
        extension = archivo.name.split('.')[-1].lower()

        # Validar formato de archivo
        if extension not in ["csv", "xlsx", "xls"]:
            messages.error(request, "Formato no soportado. Por favor, suba un archivo CSV o Excel (.xlsx, .xls).")
            return redirect(request.path)

        try:
            # Leer archivo según el formato
            if extension == "csv":
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)

            # Validar que el archivo tenga las columnas necesarias
            columnas_requeridas = ['ID', 'Nombre', 'Marca', 'No. Inventario', 'Modelo']
            if not all(col in df.columns for col in columnas_requeridas):
                messages.error(request, "El archivo no tiene las columnas correctas. Use la plantilla de importación.")
                return redirect(request.path)

            # Procesar cada fila del archivo
            for _, row in df.iterrows():
                # Obtener o crear Marca y Modelo
                marca, _ = Marca.objects.get_or_create(nombre=row['Marca'].strip()) if pd.notna(row['Marca']) else (None, None)
                modelo, _ = Modelo.objects.get_or_create(nombre=row['Modelo'].strip()) if pd.notna(row['Modelo']) else (None, None)

                # Crear o actualizar Activo
                Activo.objects.update_or_create(
                    id=row['ID'],
                    defaults={
                        'nombre': row['Nombre'],
                        'marca': marca,
                        'no_inventario': row['No. Inventario'],
                        'modelo': modelo
                    }
                )

            messages.success(request, "Activos importados correctamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")

        return redirect(request.path)

    return render(request, "admin/importar_activos.html")