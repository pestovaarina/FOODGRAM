import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient
from foodgram.settings import CSV_FILES_DIR


class Command(BaseCommand):
    help = 'Заполнение базы данных ингредиентами.'

    def import_ingredients_from_csv_file(self):
        with open(
            f'{CSV_FILES_DIR}/ingredients.csv', encoding='utf-8'
        ) as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            ingredients = [
                Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
                for row in reader
            ]
            Ingredient.objects.bulk_create(ingredients)
        self.stdout.write(self.style.SUCCESS('Успешно загружено!'))

    def handle(self, *args, **options):
        self.import_ingredients_from_csv_file()
