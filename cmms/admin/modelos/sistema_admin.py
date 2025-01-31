from django.contrib import admin
from ...models import Sistema




class HijoInline(admin.TabularInline):
    model = Sistema
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).filter(principal=True)
    
class PrincipalFilter(admin.SimpleListFilter):
    title = 'Principal'
    parameter_name = 'principal'

    def lookups(self, request, model_admin):
        # Mostrar solo los sistemas que no tienen principal en el filtro
        return [(sistema.id, sistema.nombre) for sistema in Sistema.objects.filter(principal__isnull=True)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(principal_id=self.value())
        return queryset
    

@admin.register(Sistema)
class SistemaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'principal', )
    list_filter = (PrincipalFilter, )  # Usar el filtro personalizado
    inlines = [HijoInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs  # Mostrar todos los s