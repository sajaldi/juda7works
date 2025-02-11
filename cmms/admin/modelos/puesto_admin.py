from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from ...models import Puesto



from ...models import Puesto  # Importa tu modelo Puesto

@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion','total_horas_trabajadas')
    search_fields = ('nombre', 'descripcion','total_horas_trabajadas')
    list_filter = ('nombre',)
    ordering = ('nombre',)

    actions = ['clone_puesto']

    def clone_puesto(self, request, queryset):
        if not queryset:
            self.message_user(request, "No se ha seleccionado ningún puesto para clonar.", messages.WARNING)
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        if len(queryset) > 1:
            self.message_user(request, "Solo se puede clonar un puesto a la vez.", messages.WARNING)
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        puesto_original = queryset[0]

        if request.POST.get('cantidad'):
            cantidad = int(request.POST['cantidad'])
        else:
            cantidad = 1

        for _ in range(cantidad):
            nuevo_puesto = Puesto(
                nombre=f"{puesto_original.nombre} (Clon)",
                descripcion=puesto_original.descripcion,
                # ... clona otros campos si es necesario ...
            )
            nuevo_puesto.save()

        self.message_user(request, f"Se han clonado {cantidad} puestos.", messages.SUCCESS)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    clone_puesto.short_description = "Clonar puesto (con cantidad)"
    clone_puesto.label = "Clonar puesto"

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['cantidad_form'] = True  # Indica que se debe mostrar el formulario de cantidad
        return super().changelist_view(request, extra_context=extra_context)