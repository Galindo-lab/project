from django.db import models

class Ubicacion(models.Model):
    latitud = models.CharField(max_length=50)  # Se almacena como string
    longitud = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Latitud: {self.latitud}, Longitud: {self.longitud}"