# Generated by Django 2.2.19 on 2023-09-24 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20230922_2349'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredientrecipe',
            name='count',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
