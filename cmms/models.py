from datetime import date, datetime
from django.db import models
from django.urls import reverse
from django.utils import timezone
from multiselectfield import MultiSelectField
from mptt.fields import TreeForeignKey
from django.core.exceptions import ValidationError

# Create your models here.


#
class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre
    
class Frecuencia(models.Model):
    nombre = models.CharField(max_length=50)
    intervalo = models.IntegerField()
    color = models.CharField(max_length=7, default='#007bff')
    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre  = models.CharField( max_length=50)
    principal = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategorias'
    )
    def __str__(self):
        return f"{self.nombre}  { self.principal if self.principal else ''}"

class Material(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=[('REPUESTO','Repuesto'),('EPP','Equipo de Protección Personal'),('HERRAMIENTA','herramienta')])
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, null=True)
    codigo_de_barra = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.nombre
    
    @property
    def total_cantidad(self):
        return self.movimientodeinventario_set.aggregate(total=models.Sum('cantidad'))['total'] or 0


    def cantidades_por_almacen(self):
        # Método para obtener las cantidades por almacén
        cantidades = {}
        for movimiento in self.movimientodeinventario_set.all():
            # Verificamos si el almacén existe
            if movimiento.almacen:
                if movimiento.almacen.nombre not in cantidades:
                    cantidades[movimiento.almacen.nombre] = 0
                cantidades[movimiento.almacen.nombre] += movimiento.cantidad
            else:
                # Si no tiene almacén, lo agregamos como "Sin Almacén"
                if 'Sin Almacén' not in cantidades:
                    cantidades['Sin Almacén'] = 0
                cantidades['Sin Almacén'] += movimiento.cantidad
        return cantidades


class Area(models.Model):
    nombre = models.CharField(max_length=100)
    principal = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    identificador = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
           return f"{self.principal} {self.nombre}" if self.principal else self.nombre
    
class Kit(models.Model):
    nombre= models.CharField(max_length=100)
    descripcion = models.TextField(null=True)
    materiales = models.ManyToManyField(Material)

    def __str__(self):
        return self.nombre



class HorarioPreestablecido(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    operativo = models.BooleanField(blank=True, null=True)
    noOperativo = models.BooleanField(blank=True,null=True)
    
    @property
    def total_duracion_en_minutos(self):
        return sum(dia.duracion_en_minutos for dia in self.dias_horarios.all())
    @property
    def total_duracion_en_horas(self):
        return self.total_duracion_en_minutos / 60
    
    def __str__(self):
        return self.nombre

class DiaHorario(models.Model):
    DIAS_SEMANA = [
        ('L', 'Lunes'),
        ('M', 'Martes'),
        ('X', 'Miércoles'),
        ('J', 'Jueves'),
        ('V', 'Viernes'),
        ('S', 'Sábado'),
        ('D', 'Domingo'),
    ]

    horario = models.ForeignKey(HorarioPreestablecido, on_delete=models.CASCADE, related_name="dias_horarios")
    dia = models.CharField(max_length=1, choices=DIAS_SEMANA)
    horaInicio = models.TimeField()
    horaFinal = models.TimeField()
    
    @property
    def duracion_en_minutos(self):
        delta = datetime.combine(date.min, self.horaFinal) - datetime.combine(date.min, self.horaInicio)
        return delta.total_seconds() / 60

    def __str__(self):
        return f"{dict(self.DIAS_SEMANA).get(self.dia)}: {self.horaInicio} - {self.horaFinal}"

### aqui definimos la clase de sistema y subsistema
class Sistema(models.Model):
    nombre = models.CharField(max_length=100)
    principal = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subsistemas')

    def __str__(self):
        return f"{self.principal} {self.nombre}" if self.principal else self.nombre

class HojaDeRuta(models.Model):
    descripcion = models.TextField(null=True)
    
    #plandemantenimiento = models.ForeignKey(PlanDeMantenimiento, on_delete=models.CASCADE, null=True)
    intervalo = models.ForeignKey(Frecuencia,on_delete=models.CASCADE, null=True, blank=True)
    sistema = models.ForeignKey(Sistema, on_delete=models.CASCADE, null=True, blank=True)  # Agrega esta línea
    #areas = models.ManyToManyField(Area, related_name='hojas_de_ruta', blank=True)  # Relación Muchos a Muchos
    nombre = models.CharField(max_length=100)
    horario = models.ForeignKey(HorarioPreestablecido, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.nombre
    
    def sumatoria_tiempo_pasos(self):
        # Obtiene la suma total de los tiempos de los pasos asociados a esta hoja de ruta
        total_time = self.pasoshojaderuta_set.aggregate(models.Sum('tiempo'))['tiempo__sum']
        return total_time if total_time is not None else 0  # Retorna 0 si no hay tiempo calculado

    sumatoria_tiempo_pasos.short_description = "Tiempo Total Pasos"

class PasosHojaDeRuta(models.Model):
    paso = models.CharField(max_length=100)
    tiempo = models.IntegerField(null=True)
    hojaderuta = models.ForeignKey(HojaDeRuta, on_delete=models.CASCADE)

    def __str__(self):
        return self.paso
    

    

class Modelo(models.Model):
    nombre = models.CharField(max_length=100)
    marca = models.ForeignKey(Marca,on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria,on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.nombre

class Activo(models.Model):
    nombre = models.CharField(max_length=100)
    marca = models.ForeignKey(Marca,on_delete=models.CASCADE, null=True)
    no_inventario = models.CharField(max_length=100, null=True, unique=True)
    modelo = models.ForeignKey(Modelo,on_delete= models.CASCADE,null=True)
    area = models.ForeignKey(Area,on_delete=models.CASCADE, null=True)
    hojasderuta = models.ManyToManyField(HojaDeRuta,related_name='hojaderuta', blank=True)
    def __str__(self):
        return self.nombre
    
    

class Programacion(models.Model):
    nombre = models.CharField(max_length=100)
    HojaDeRuta = models.ForeignKey(HojaDeRuta,on_delete=models.CASCADE)
    fechaDeInicio = models.DateTimeField(default= timezone.now )
    fecha_final = models.DateTimeField(null=True)  # Agregar el campo fecha_final
    areas = models.ManyToManyField(Area, related_name='programacion', blank=True)  # Relación Muchos a Muchos
    activos = models.ManyToManyField(Activo, related_name='programacion',blank=True)
    programado = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Programación"
        verbose_name_plural = "Programaciones"

    def __str__(self):
        return self.nombre
    

class OrdenDeTrabajo(models.Model):
    nombre = models.CharField(max_length=100)
    HojaDeRuta =models.ForeignKey(HojaDeRuta, on_delete=models.CASCADE, null=True, blank=True)
    fechaDeInicio = models.DateTimeField(null=True, blank=True)
    fechaDeFin = models.DateTimeField(null=True, blank=True)

    programacion =models.ForeignKey("cmms.Programacion", verbose_name=("programacion"), on_delete=models.CASCADE, null=True)
    area = models.ForeignKey(Area,on_delete=models.CASCADE,null=True)
    def __str__(self):
        
        return self.nombre

class Semana(models.Model):
    nombre = models.CharField(max_length=2)  # S1, S2, etc.
    fecha_inicial = models.DateField()
    fecha_final = models.DateField()

    def __str__(self):
        return self.nombre

# Asegúrate de que el resto del archivo esté correctamente configurado
verbose_name_plural = "Programaciones"

def __str__(self):
    return self.nombre



class PuntoDeMedicion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
###aqui ya definimos una nueva clase o modelo.


class Empresa(models.Model):
    nombre = models.CharField(max_length=250)

    def __str__(self):
        return self.nombre
    

class Almacen(models.Model):
    nombre= models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    

class Persona(models.Model):
    nombre= models.CharField(max_length=250)
    empresa = models.ForeignKey(Empresa,on_delete=models.CASCADE, null=True)
    dni = models.CharField(max_length=13,null=True)

    def __str__(self):
        return self.nombre
    

class MovimientoDeInventario(models.Model):
    TIPO_TRANSACCION_CHOICES = [
        ('INGRESO', 'Ingreso de Material'),
        ('AJUSTE', 'Ajuste de Inventario'),
        ('DESPACHO', 'Despacho de Material'),
    ]
    almacen = models.ForeignKey(Almacen, verbose_name="Almacen", on_delete=models.CASCADE, null=True)
    movimiento = models.CharField(max_length=100)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fecha_de_transaccion = models.DateTimeField(auto_now=False, auto_now_add=False)
    tipo_de_transaccion = models.CharField(
        max_length=20,
        choices=TIPO_TRANSACCION_CHOICES,
        default='INGRESO',  # Opción predeterminada
    )

    def clean(self):
        # Si el tipo de movimiento es "Despacho de Material", verificamos si hay suficiente cantidad disponible
        if self.tipo_de_transaccion == 'Despacho de Material':
            cantidad_disponible = self.material.cantidades_por_almacen().get(self.almacen.nombre, 0)
            if self.cantidad > cantidad_disponible:
                raise ValidationError(f'La cantidad a despachar ({self.cantidad}) es mayor que la cantidad disponible en el almacén "{self.almacen.nombre}" ({cantidad_disponible}).')
            

    def save(self, *args, **kwargs):
        self.full_clean()  # Llamamos a clean() para que se ejecuten las validaciones
        # Si el tipo de transacción es "DESPACHO", aseguramos que la cantidad sea negativa
        if self.tipo_de_transaccion == 'DESPACHO':
            self.cantidad = abs(self.cantidad) * -1  # Hacemos la cantidad negativa

        super().save(*args, **kwargs)  # Llamamos al método save original

    def __str__(self):
        return f"{self.movimiento} ({self.get_tipo_de_transaccion_display()})"