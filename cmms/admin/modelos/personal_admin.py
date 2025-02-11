

from django.contrib import admin

from ...models import Personal

@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido','dni' )
    search_fields = ('nombre', 'apellido','dni' )
    
    
