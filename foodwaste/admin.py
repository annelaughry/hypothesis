from django.contrib import admin
from .models import Dish, FoodEntry, DishWaste, DishReport

admin.site.register(Dish)
admin.site.register(FoodEntry)
admin.site.register(DishWaste)
admin.site.register(DishReport)
