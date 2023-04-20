"""
Custom manage-commands.
"""

import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag

MODELS_FILES = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv',
}


class Command(BaseCommand):
    '''
    Load data from csv into DB.
    Raise ALREDY_LOADED_ERROR_MESSAGE if data exists in DB.
    '''

    help = settings.HELP_MESSAGE

    def handle(self, *args, **options):

        if Ingredient.objects.exists() or Tag.objects.exists():
            print(settings.ALREDY_LOADED_ERROR_MESSAGE)
            return

        print("Loading data...")

        for model, file in MODELS_FILES.items():
            with open(
                    f'{settings.DIRECTION_OF_FILES}/{file}',
                    'r', encoding='utf-8',
            ) as table:
                reader = csv.DictReader(table)
                model.objects.bulk_create(model(**data) for data in reader)

        print("Loading data complete")
