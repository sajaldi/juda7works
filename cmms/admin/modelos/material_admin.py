
from django.contrib import admin
from ...models import  KitDeHerramientas, Material
"""
 nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=[('REPUESTO','Repuesto'),('EPP','Equipo de Protección Personal'),('HERRAMIENTA','herramienta')])
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, null=True)
    codigo_de_barra = models.CharField(max_length=100, null=True)
"""


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion','tipo','marca','codigo_de_barra')
    search_fields = ('nombre', 'descripcion','tipo','marca','codigo_de_barra')
    list_filter = ('tipo',)

    
    ordering = ('nombre',)
    

"""
 nombre = models.CharField(max_length=100, unique=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True)
    descripcion = models.TextField(null=True)
    """

