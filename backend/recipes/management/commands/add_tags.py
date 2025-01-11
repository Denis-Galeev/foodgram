import csv

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импорт тегов из CSV файла.'

    def handle(self, *args, **options):
        with open('data/tags.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',')
            existing_slugs = set(Tag.objects.values_list('slug', flat=True))

            new_tags = [
                Tag(name=name, slug=slug)
                for name, slug in reader
                if slug not in existing_slugs and name
            ]

            if new_tags:
                Tag.objects.bulk_create(new_tags)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Добавлено {len(new_tags)} новых тегов.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Новых тегов для добавления нет.')
                )
