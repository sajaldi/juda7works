# Generated by Django 5.1.3 on 2025-01-30 08:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmms', '0003_remove_hojaderuta_plandemantenimiento_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hojaderuta',
            name='areas',
        ),
        migrations.RemoveField(
            model_name='hojaderuta',
            name='frecuencia',
        ),
    ]
