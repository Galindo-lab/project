from django.contrib import admin

from core.models import Ubicacion

# Register your models here.
@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'latitud', 'longitud')  # Campos a mostrar en la lista
    search_fields = ('latitud', 'longitud')      # Campos por los que se puede buscar
    list_per_page = 20     