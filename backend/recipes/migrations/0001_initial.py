# Generated by Django 4.2 on 2023-04-06 14:47

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Favorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "added",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="time of adding"
                    ),
                ),
            ],
            options={
                "verbose_name": "Recipes in favorite",
                "verbose_name_plural": "Recipes in favorite",
                "ordering": ["-added"],
            },
        ),
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="name")),
                (
                    "measurement_unit",
                    models.CharField(max_length=200, verbose_name="measurement_unit"),
                ),
            ],
            options={
                "verbose_name": "Ingredient",
                "verbose_name_plural": "Ingredients",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="IngredientRecipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.PositiveIntegerField(verbose_name="amount")),
            ],
            options={
                "verbose_name": "Ingredients in recipe",
                "verbose_name_plural": "Ingredients in recipe",
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="name")),
                (
                    "image",
                    models.ImageField(upload_to="recipes/", verbose_name="image"),
                ),
                ("text", models.TextField(verbose_name="text")),
                (
                    "cooking_time",
                    models.PositiveSmallIntegerField(
                        default=1,
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="cooking_time",
                    ),
                ),
                (
                    "pub_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="publication date"
                    ),
                ),
            ],
            options={
                "verbose_name": "Recipe",
                "verbose_name_plural": "Recipes",
                "ordering": ("-pub_date",),
            },
        ),
        migrations.CreateModel(
            name="RecipeTag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tags in recipe",
                "verbose_name_plural": "Tags in recipe",
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=200, unique=True, verbose_name="name"),
                ),
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("#0000FF", "Голубой"),
                            ("#FF0000", "Красный"),
                            ("#008000", "Зеленый"),
                            ("#FFFF00", "Желтый"),
                            ("#8775D2", "Фиолетовый"),
                        ],
                        max_length=7,
                        unique=True,
                        verbose_name="color",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(max_length=200, unique=True, verbose_name="slug"),
                ),
            ],
            options={
                "verbose_name": "Tag",
                "verbose_name_plural": "Tags",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="ShoppingCart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "added",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="time of adding"
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipe_in_shopping_cart",
                        to="recipes.recipe",
                        verbose_name="recipe",
                    ),
                ),
            ],
            options={
                "verbose_name": "Recipes in shopping cart",
                "verbose_name_plural": "Recipes in shopping cart",
                "ordering": ["-added"],
            },
        ),
    ]
