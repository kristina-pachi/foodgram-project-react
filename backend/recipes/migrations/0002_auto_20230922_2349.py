# Generated by Django 2.2.19 on 2023-09-22 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['name']},
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='quantity',
        ),
    ]
