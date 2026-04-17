from django.shortcuts import render, redirect
from .forms import FoodEntryForm
from .models import FoodEntry, DishWaste, Dish
from django.contrib import messages
from collections import defaultdict


def home_view(request):
    return render(request, 'foodwaste/home.html')


def food_entry_view(request):
    if request.method == 'POST':
        form = FoodEntryForm(request.POST)
        if form.is_valid():
            food_entry = form.save(commit=False)
            food_entry.user = request.user if request.user.is_authenticated else None
            food_entry.save()
            form.save_m2m()

            # Handle new dish input
            new_dish_name = form.cleaned_data.get('new_dish')
            if new_dish_name:
                new_dish_name = new_dish_name.strip()
                if new_dish_name:
                    dish, created = Dish.objects.get_or_create(name__iexact=new_dish_name, defaults={'name': new_dish_name})
                    food_entry.dishes.add(dish)

            # Save DishWaste for all selected dishes
            for dish in food_entry.dishes.all():
                waste_key = f"waste_percentage_{dish.id}"
                rating_key = f"dish_{dish.id}_rating"

                waste_val = int(request.POST.get(waste_key, 0))
                rating_val = int(request.POST.get(rating_key, 0))

                DishWaste.objects.create(
                    food_entry=food_entry,
                    dish=dish,
                    waste_percentage=waste_val,
                    rating=rating_val
                )

            messages.success(request, "Thank you! Your submission has been recorded.")
            return redirect('foodwaste:home')
    else:
        form = FoodEntryForm()

    return render(request, 'foodwaste/food_entry.html', {'form': form})



def report_view(request):
    dish_stats = defaultdict(lambda: {"total_waste": 0, "num_entries": 0, "ratings": []})

    all_entries = FoodEntry.objects.prefetch_related('dishes', 'dish_wastes')

    for entry in all_entries:
        for dish_waste in entry.dish_wastes.all():
            dish_name = dish_waste.dish.name.capitalize()
            dish_stats[dish_name]["total_waste"] += dish_waste.waste_percentage
            dish_stats[dish_name]["num_entries"] += 1
            dish_stats[dish_name]["ratings"].append(dish_waste.rating)

    # Format the report
    formatted_report = []
    for dish, data in dish_stats.items():
        num_entries = data["num_entries"]
        avg_waste = round(data["total_waste"] / num_entries, 1) if num_entries else 0

        ratings = data["ratings"]
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0

        formatted_report.append({
            "dish": dish,
            "average_rating": avg_rating,
            "total_waste": avg_waste
        })

    formatted_report.sort(key=lambda x: x["average_rating"], reverse=True)

    return render(request, "foodwaste/report.html", {"report_data": formatted_report})


def full_report_view(request):
    entries = FoodEntry.objects.all().order_by('-date')
    return render(request, "foodwaste/full_report.html", {"entries": entries})
