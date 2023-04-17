# Generated by Django 4.2 on 2023-04-17 05:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoppingcart",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shopping_cart",
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AddField(
            model_name="recipeingredient",
            name="ingredient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="recipes.ingredient",
                verbose_name="ingredient",
            ),
        ),
        migrations.AddField(
            model_name="recipeingredient",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipe_ingredient",
                to="recipes.recipe",
                verbose_name="recipes",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="recipes",
                to=settings.AUTH_USER_MODEL,
                verbose_name="author",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="ingredients",
            field=models.ManyToManyField(
                related_name="recipe",
                through="recipes.RecipeIngredient",
                to="recipes.ingredient",
                verbose_name="ingredients",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(
                related_name="recipes", to="recipes.tag", verbose_name="tags"
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorite",
                to="recipes.recipe",
                verbose_name="recipe",
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorite",
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AddConstraint(
            model_name="shoppingcart",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique recipe in shopping cart"
            ),
        ),
        migrations.AddConstraint(
            model_name="recipeingredient",
            constraint=models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="unique ingredient for recipe"
            ),
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique favorite"
            ),
        ),
    ]