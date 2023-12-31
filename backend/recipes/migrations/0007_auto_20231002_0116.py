# Generated by Django 3.2.16 on 2023-10-01 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20230928_0324'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['author', 'tags__slug', 'cooking_time']},
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='units',
            new_name='measurement_unit',
        ),
        migrations.RenameField(
            model_name='ingredientrecipe',
            old_name='count',
            new_name='amount',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
        migrations.AlterUniqueTogether(
            name='ingredient',
            unique_together={('name', 'measurement_unit')},
        ),
    ]
