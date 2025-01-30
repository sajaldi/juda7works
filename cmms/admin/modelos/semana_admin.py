from django.contrib import admin
from datetime import date, timedelta
from ...models import Semana

class SemanaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicial', 'fecha_final')
    search_fields = ('nombre',)
    list_filter = ('fecha_inicial', 'fecha_final')
    actions = ['generar_semanas_2025']

    def generar_semanas_2025(self, request, queryset):
        year = 2025
        start_date = date(year, 1, 1)
        
        # Asegurarse de que el primer día sea un lunes
        while start_date.weekday() != 0:
            start_date += timedelta(days=1)
        
        week_num = start_date.isocalendar()[1]
        
        for _ in range(1, 53):
            end_date = start_date + timedelta(days=6)
            
            Semana.objects.create(
                nombre=f'S{week_num}',
                fecha_inicial=start_date,
                fecha_final=end_date
            )
            start_date = end_date + timedelta(days=1)
            week_num += 1
        
        self.message_user(request, "Se han generado todas las semanas del año 2025.")

    generar_semanas_2025.short_description = "Generar todas las semanas del año 2025"

admin.site.register(Semana, SemanaAdmin)