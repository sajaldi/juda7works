from django import forms
from .models import Programacion, Activo, Categoria

class ProgramacionForm(forms.ModelForm):

    class Meta:
        model = Programacion
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Inicialmente, vaciar la lista de activos para optimizar la carga
     
      