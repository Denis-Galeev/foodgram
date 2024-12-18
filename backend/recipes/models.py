from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    pass


class Ingredient(models.Model):
    pass


class Recipe(models.Model):
    pass
