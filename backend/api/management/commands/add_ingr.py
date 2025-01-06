import csv

from django.core.management.base import BaseCommand

from api.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('data/ingredients.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',')
            new_ingredient = [
                Ingredient(name=name, measurement_unit=unit)
                for name, unit in reader
                if name
            ]
            if new_ingredient:
                Ingredient.objects.bulk_create(new_ingredient)
