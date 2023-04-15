"""
Custom manage-commands.
"""

import csv

from django.core.management import BaseCommand
from recipes.models import Ingredient, Tag

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""

DIR = './data/'
MODELS_FILES = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv',
}


class Command(BaseCommand):
    '''
    Load data from csv into DB.
    Raise ALREDY_LOADED_ERROR_MESSAGE if data exists in DB.
    '''

    help = "Loads data from .csv-files"

    def handle(self, *args, **options):

        if Ingredient.objects.exists() or Tag.objects.exists():
            print('Data already exists.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        print("Loading data...")

        for model, file in MODELS_FILES.items():
            with open(
                    f'{DIR}/{file}',
                    'r', encoding='utf-8',
            ) as table:
                reader = csv.DictReader(table)
                model.objects.bulk_create(model(**data) for data in reader)

        print("Loading data complete")
