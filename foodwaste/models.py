from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Dish Model
class Dish(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# FoodEntry Model – one entry per student submission
class FoodEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    dishes = models.ManyToManyField(Dish)
    waste_reason = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        dishes_list = ", ".join([dish.name for dish in self.dishes.all()])
        user = self.user.username if self.user else "Anonymous"
        return f"{user} – {dishes_list} – {self.date}"

# DishWaste – links each dish to its waste % and rating per entry
class DishWaste(models.Model):
    food_entry = models.ForeignKey(FoodEntry, on_delete=models.CASCADE, related_name='dish_wastes')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    waste_percentage = models.PositiveSmallIntegerField(choices=[
        (0, '0%'), (25, '25%'), (50, '50%'), (75, '75%'), (100, '100%')
    ])
    rating = models.PositiveSmallIntegerField(choices=[
        (1, '1 ⭐'), (2, '2 ⭐'), (3, '3 ⭐'), (4, '4 ⭐'), (5, '5 ⭐')
    ], default=0)

    class Meta:
        unique_together = ('food_entry', 'dish')

    def __str__(self):
        return f"{self.dish.name} ({self.waste_percentage}% waste, {self.rating}⭐)"

# Optional summary model (not used yet, but good for aggregation)
class DishReport(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    total_waste = models.FloatField(default=0.0)
    average_rating = models.FloatField(default=0.0)
    report_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.dish.name} on {self.report_date}"
