# Generated by Django 5.1.6 on 2025-04-16 03:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_ubicacion_latitud_alter_ubicacion_longitud'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Ubicacion',
        ),
    ]
