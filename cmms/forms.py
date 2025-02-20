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

from django.apps import apps
class ImportForm(forms.Form):
    """Formulario para la importación de datos desde Excel."""
    model_choices = [(model.__name__, model.__name__) for model in apps.get_app_config('cmms').get_models()]
    model = forms.ChoiceField(choices=model_choices, label="Seleccionar modelo")
    file = forms.FileField(label="Archivo Excel")

class ExportForm(forms.Form):
    """Formulario para la exportación de datos a Excel."""
    model_choices = [(model.__name__, model.__name__) for model in apps.get_app_config('cmms').get_models()]
    model = forms.ChoiceField(choices=model_choices, label="Seleccionar modelo")