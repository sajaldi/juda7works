# Generated by Django 5.1.3 on 2025-02-14 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmms', '0035_alter_sistema_nombre'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaHerramienta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='herramienta',
            name='material',
        ),
    ]
