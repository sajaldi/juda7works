

# Importar librerías
import csv
from django.shortcuts import redirect, render
from django.contrib import messages

from ..models import Activo


def importar_activos_view(request):
    """
    Vista para cargar y procesar el archivo CSV.
    """
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        
        # Leer y procesar el archivo CSV
        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)

            actualizados = 0
            no_encontrados = []
            
            for row in reader:
                try:
                    activo = Activo.objects.get(id=row["id"])
                    cambios = []
                    for field in ["nombre", "marca", "no_inventario", "modelo"]:
                        nuevo_valor = row[field]
                        if nuevo_valor != getattr(activo, field):
                            setattr(activo, field, nuevo_valor)
                            cambios.append(field)

                    if cambios:
                        activo.save()
                        actualizados += 1
                except Activo.DoesNotExist:
                    no_encontrados.append(row["id"])

            # Mensajes
            if actualizados > 0:
                messages.success(request, f"Se actualizaron {actualizados} activos correctamente.")
            if no_encontrados:
                messages.warning(request, f"No se encontraron {len(no_encontrados)} activos con los IDs: {', '.join(no_encontrados)}")

        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")
        return redirect("..")  # Redirigir de vuelta al admin

    return render(request, "admin/importar_activos.html")

    importar_activos.short_description = "Importar y actualizar activos desde CSV"