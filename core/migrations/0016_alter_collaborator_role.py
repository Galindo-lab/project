# Generated by Django 5.1.6 on 2025-05-15 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_remove_task_dependencies_task_predecessor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collaborator',
            name='role',
            field=models.CharField(choices=[('ver', 'Ver'), ('editar', 'Editar')], max_length=10),
        ),
    ]
