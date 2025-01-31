# filepath: /C:/Django/SoftCoMJuda/Softcom/cmms/views/hoja_de_ruta_views.py
from django.shortcuts import render
from django.http import HttpResponse
from openpyxl import Workbook, load_workbook
from cmms.models import HojaDeRuta, Sistema
def exportar_plantilla_hojaderuta(request):
    # Crear un libro de trabajo y una hoja
    wb = Workbook()
    ws = wb.active
    ws.title = "Plantilla de Exportación de HojaDeRuta"

    # Agregar encabezados
    headers = ["ID", "Nombre", "Descripción", "Intervalo", "Sistema", "Horario"]
    ws.append(headers)

    # Obtener los datos del modelo HojaDeRuta
    hojas_de_ruta = HojaDeRuta.objects.all()
    for hoja in hojas_de_ruta:
        intervalo_nombre = hoja.intervalo if hoja.intervalo else ''
        sistema_nombre = hoja.sistema.nombre if hoja.sistema else ''
        horario_nombre = hoja.horario.nombre if hoja.horario else ''
        ws.append([hoja.id, hoja.nombre, hoja.descripcion, intervalo_nombre, sistema_nombre, horario_nombre])

    # Configurar la respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=plantilla_exportacion_hojaderuta.xlsx'

    # Guardar el libro de trabajo en la respuesta
    wb.save(response)
    return response



def importar_plantilla_hojaderuta(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        wb = load_workbook(uploaded_file)
        ws = wb.active

        errores = []

        # Leer los datos del archivo Excel
        for row in ws.iter_rows(min_row=2, values_only=True):
            hoja_id, nombre, descripcion, intervalo_nombre, sistema_nombre, horario_nombre = row

            # Obtener o crear el intervalo
            if intervalo_nombre:
                intervalo, created = HojaDeRuta.intervalo.objects.get_or_create(nombre=intervalo_nombre)
            else:
                intervalo = None

            # Obtener o crear el sistema
            if sistema_nombre:
                sistema, created = Sistema.objects.get_or_create(nombre=sistema_nombre)
            else:
                sistema = None

            # Obtener o crear el horario
            if horario_nombre:
                horario, created = HojaDeRuta.HorarioPreestablecido.objects.get_or_create(nombre=horario_nombre)
            else:
                horario = None

            # Actualizar o crear la hoja de ruta
            HojaDeRuta.objects.update_or_create(
                id=hoja_id,
                defaults={'nombre': nombre, 'descripcion': descripcion, 'intervalo': intervalo, 'sistema': sistema, 'horario': horario}
            )

        context = {
            'errores': errores,
        }
        return render(request, 'cmms/importar_hojaderuta.html', context)

    return render(request, 'cmms/importar_hojaderuta.html')
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        wb = load_workbook(uploaded_file)
        ws = wb.active

        errores = []

        # Leer los datos del archivo Excel
        for row in ws.iter_rows(min_row=2, values_only=True):
            hoja_id, nombre, descripcion, intervalo, sistema_nombre, horario_nombre = row

            # Obtener o crear el sistema
            if sistema_nombre:
                sistema, created = Sistema.objects.get_or_create(nombre=sistema_nombre)
            else:
                sistema = None

            # Obtener o crear el horario
            if horario_nombre:
                horario, created = HojaDeRuta.horario.objects.get_or_create(nombre=horario_nombre)
            else:
                horario = None

            # Actualizar o crear la hoja de ruta
            HojaDeRuta.objects.update_or_create(
                id=hoja_id,
                defaults={'nombre': nombre, 'descripcion': descripcion, 'intervalo': intervalo, 'sistema': sistema, 'horario': horario}
            )

        context = {
            'errores': errores,
        }
        return render(request, 'cmms/importar_hojaderuta.html', context)

    return render(request, 'cmms/importar_hojaderuta.html')