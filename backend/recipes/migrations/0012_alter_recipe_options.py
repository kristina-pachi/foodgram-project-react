# Generated by Django 3.2.16 on 2023-11-04 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_alter_recipe_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-id']},
        ),
    ]