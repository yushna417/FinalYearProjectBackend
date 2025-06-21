import os
import django
import csv

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TarkariDeal.settings')  # Replace with your project name
django.setup()

from Vegetable.models import Veg

# Open and read the CSV file
with open('D:/Honours/TarkariDeal/vegetables.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        Veg.objects.get_or_create(name=row['Vegetable'], unit=row['Unit'])

print("✅ Vegetables imported successfully.")
