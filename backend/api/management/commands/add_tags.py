import csv

from django.core.management.base import BaseCommand

from api.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('data/tags.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',')
            new_tags = [
                Tag(name=name, slug=slug)
                for name, slug in reader
                if name
            ]
            if new_tags:
                Tag.objects.bulk_create(new_tags)
