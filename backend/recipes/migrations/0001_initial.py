# Generated by Django 4.2 on 2023-04-17 05:27

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
                    "date_added",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="time of adding"
                    ),
                ),
            ],
            options={
                "verbose_name": "Recipes in favorite",
                "verbose_name_plural": "Recipes in favorite",
                "ordering": ["-date_added"],
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
                ("text", models.TextField(max_length=1000, verbose_name="text")),
                (
                    "cooking_time",
                    models.PositiveSmallIntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(300),
                        ],
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
            name="RecipeIngredient",
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
                    "amount",
                    models.PositiveSmallIntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5000),
                        ],
                        verbose_name="amount",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ingredient in recipe",
                "verbose_name_plural": "Ingredient in recipe",
                "ordering": ("recipe",),
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
                    models.SlugField(
                        db_index=False, max_length=200, unique=True, verbose_name="slug"
                    ),
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
                    "date_added",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="time of adding"
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shopping_cart",
                        to="recipes.recipe",
                        verbose_name="recipes",
                    ),
                ),
            ],
            options={
                "verbose_name": "Recipes in shopping cart",
                "verbose_name_plural": "Recipes in shopping cart",
                "ordering": ["-date_added"],
            },
        ),
    ]
