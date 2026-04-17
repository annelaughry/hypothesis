# foodwaste/management/commands/load_initial_dishes.py
from django.core.management import call_command
from django.core.management.base import BaseCommand
from foodwaste.models import Dish

class Command(BaseCommand):
    help = "Loads initial dish data if it doesn't already exist."

    def handle(self, *args, **kwargs):
        if Dish.objects.exists():
            self.stdout.write(self.style.NOTICE("Dishes already exist, skipping loaddata."))
        else:
            call_command("loaddata", "foodwaste/fixtures/initial_dishes.json")
            self.stdout.write(self.style.SUCCESS("Loaded initial dish data."))
