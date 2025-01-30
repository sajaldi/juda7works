from django.contrib import admin
from ...models import OrdenDeTrabajo

@admin.register(OrdenDeTrabajo)
class OrdenDeTrabajoAdmin(admin.ModelAdmin):
    list_display = ('nombre','HojaDeRuta','fechaDeInicio','fechaDeFin','area')
    