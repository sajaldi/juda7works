

from django import forms
from django.contrib import admin
from ...models import KitDeHerramientas, Herramienta
from django.utils.safestring import mark_safe

class HerramientasCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        herramientas_por_categoria = {}
        
        # Organiza las herramientas por categoría
        for herramienta in Herramienta.objects.all():
            categoria_nombre = herramienta.categoria.nombre if herramienta.categoria else "Sin Categoría"
            if categoria_nombre not in herramientas_por_categoria:
                herramientas_por_categoria[categoria_nombre] = []
            herramientas_por_categoria[categoria_nombre].append((herramienta.id, herramienta.nombre))
        
        # Genera el HTML asegurando el formato correcto para Django
        for categoria, herramientas in herramientas_por_categoria.items():
            output.append(f'<div class="categoria-group">')
            output.append(f'<h4 class="categoria-titulo" onclick="toggleCategoria(this)">{categoria}</h4>')
            output.append('<div class="categoria-contenido" style="display:none;">')
            for herramienta_id, herramienta_nombre in herramientas:
                checked = 'checked' if value and str(herramienta_id) in [str(v) for v in value] else ''
                output.append(
                    f'<label><input type="checkbox" name="{name}" value="{herramienta_id}" {checked}> {herramienta_nombre}</label><br>'
                )
            output.append('</div>')
            output.append('</div>')
        
        # Agrega un campo oculto para asegurar el envío del POST
        #output.append(f'<input type="hidden" name="{name}" value="">')
        
        return mark_safe('\n'.join(output))

    
class KitHerramientasForm(forms.ModelForm):
    herramientas = forms.ModelMultipleChoiceField(
        queryset=Herramienta.objects.all(),
        widget=HerramientasCheckboxSelectMultiple()
    )

    class Meta:
        model = KitDeHerramientas
        fields = '__all__'

    def clean_herramientas(self):
        herramientas = self.cleaned_data.get('herramientas')
        # Asegura que solo IDs sean retornados
        return [herramienta.id for herramienta in herramientas]

    def save(self, commit=True):
        instancia = super().save(commit=False)
        # Guarda las herramientas seleccionadas correctamente
        instancia.save()
        self.cleaned_data['herramientas'] = self.cleaned_data.get('herramientas', [])
        instancia.herramientas.set(self.cleaned_data['herramientas'])
        return instancia

    class Media:
        css = {
            'all': ('css/kitdeherramientas.css',)
        }
        js = ('js/kitdeherramientas.js',)

    

@admin.register(KitDeHerramientas)
class KitDeHerramientasAdmin(admin.ModelAdmin):
    form = KitHerramientasForm
    list_display = ('clave_kit','nombre', 'descripcion',)
    search_fields = ('nombre', 'descripcion')
  
    ordering = ('nombre',)




@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ('nombre',  'descripcion', 'marca')
    search_fields = ('nombre', 'marca')
    list_filter = ('marca',)

