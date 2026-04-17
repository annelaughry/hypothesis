
import csv
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Dataset, DataRow

@receiver(post_save, sender=Dataset)
def parse_csv_on_upload(sender, instance, created, **kwargs):
    if instance.uploaded_csv:
        # Optional: clear old rows if re-uploading
        instance.rows.all().delete()

        try:
            file = instance.uploaded_csv.open("r")
            reader = csv.DictReader(file)

            for row in reader:
                DataRow.objects.create(dataset=instance, data=row)

        except Exception as e:
            print("CSV parsing error:", e)
