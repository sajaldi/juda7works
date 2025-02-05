#Model Admin de pasos de hoja de ruta 
import csv
from django.contrib import admin
from django.http import HttpResponse
import openpyxl
from ...models import PasosHojaDeRuta



@admin.register(PasosHojaDeRuta)
class PasosHojaDeRutaAdmin(admin.ModelAdmin):
    list_display = ('paso', 'tiempo', 'hojaderuta', )
    search_fields = ('hojaderuta', )   

#paso = models.CharField(max_length=100)
  #  tiempo = models.IntegerField(null=True)
  #  hojaderuta = models.ForeignKey(HojaDeRuta, on_delete=models.CASCADE)
