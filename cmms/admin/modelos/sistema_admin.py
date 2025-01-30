from django.contrib import admin
from ...models import Sistema




class HijoInline(admin.TabularInline):
    model = Sistema
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).filter(principal=True)
    

@admin.register(Sistema)
class SistemaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'principal', )
    inlines = [HijoInline]