from django import forms
from .models import DiaHorario, HorarioPreestablecido, Programacion, Activo, Categoria

from django import forms
from .models import HorarioPreestablecido, Programacion

class ProgramacionForm(forms.ModelForm):
    # Campo para la búsqueda de horarios
    busqueda_horario = forms.CharField(
        label='Buscar Horario',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Buscar horarios...', 'class': 'form-control'})
    )

    horario = forms.ModelChoiceField(
        queryset=HorarioPreestablecido.objects.all(),
        widget=forms.RadioSelect,
        required=False
    )

    class Meta:
        model = Programacion
        fields = ['nombre', 'HojaDeRuta', 'fechaDeInicio', 'fecha_final', 'areas', 'activos', 'horario']
        widgets = {
            'areas': forms.CheckboxSelectMultiple, # Widget de checkboxes para selección múltiple
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar los horarios si hay una búsqueda
        if 'busqueda_horario' in self.data:
            busqueda = self.data.get('busqueda_horario')
            self.fields['horario'].queryset = HorarioPreestablecido.objects.filter(nombre__icontains=busqueda)
        # Si hay un horario previamente seleccionado, no hacer cambios
        elif 'horario' in self.initial:
            horario = self.initial['horario']
