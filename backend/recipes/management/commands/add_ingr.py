import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из CSV файла.'

    def handle(self, *args, **options):
        with open('data/ingredients.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',')
            existing_ingredients = set(
                Ingredient.objects.values_list('name', 'measurement_unit')
            )

            new_ingredients = [
                Ingredient(name=name.strip(), measurement_unit=unit.strip())
                for name, unit in reader
                if (name.strip(), unit.strip()) not in existing_ingredients
                and name
            ]

            if new_ingredients:
                Ingredient.objects.bulk_create(new_ingredients)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Добавлено {len(new_ingredients)} новых записей.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Новых записей для добавления нет.')
                )
