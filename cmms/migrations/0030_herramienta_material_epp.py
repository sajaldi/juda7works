# Generated by Django 5.1.3 on 2025-02-11 07:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmms', '0029_remove_cuadrilla_personal_cuadrilla_puestos_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='herramienta',
            name='material',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cmms.material'),
        ),
        migrations.CreateModel(
            name='EPP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(null=True)),
                ('material', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cmms.material')),
            ],
        ),
    ]
