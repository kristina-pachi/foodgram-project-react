from django.core.management.base import BaseCommand
from csv import DictReader
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Loads data from data/*.csv"

    def handle(self, *args, **options):
        print("====== Loading data... =====")

        for row in DictReader(
                open('data/ingredients.csv', encoding='utf8')):
            ingredient, created = Ingredient.objects.get_or_create(
                name=row['name'],
                units=row['units']
            )
            if created:
                print(f'Ingredient {ingredient.name} created')
            else:
                print(f'Ingredient {ingredient.name} exists.')
        print('===== Ingredients uploaded =====')
