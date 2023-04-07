"""
Custom manage-commands.
"""

from django.core.management import BaseCommand

from recipes.models import Ingredient


ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""

DIR = './data/'


class Command(BaseCommand):
    '''
    Load data from csv into DB.
    Raise ALREDY_LOADED_ERROR_MESSAGE if data exists in DB.
    '''

    help = "Loads data from .csv-files"

    def handle(self, *args, **options):

        if Ingredient.objects.exists():
            print('Data already exists.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        print("Loading data...")

        for row in open(DIR + 'ingredients.csv'):
            data = row.split(",")
            Ingredient.objects.get_or_create(
                name=data[0],
                measurement_unit=data[1]
            )

        print("Loading data complete")
