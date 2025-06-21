import os
import django
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TarkariDeal.settings')  
django.setup()

from Vegetable.models import Veg, DailyPrice


session = requests.Session()

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

session.get("https://kalimatimarket.gov.np/lang/en", headers=headers)

url = f'https://kalimatimarket.gov.np/price'
response = session.get(url, headers=headers)
html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')
data = soup.find_all('tr')

VegetablePrice = []
for value in data:
    cells = value.find_all(['td'])
    cell_data = [cell.get_text(strip=True) for cell in cells]
    if cell_data:
        VegetablePrice.append(cell_data)

# Save to DB
today = date.today()
for row in VegetablePrice:
    if len(row) < 5:
        continue
    name, unit, min_p, max_p, avg_p = row
    try:
        min_price = float(min_p.replace("Rs", "").strip())
        max_price = float(max_p.replace("Rs", "").strip())
        avg_price = float(avg_p.replace("Rs", "").strip())
    except ValueError:
        continue

    veg, _ = Veg.objects.get_or_create(name=name, unit=unit)
    if not DailyPrice.objects.filter(vegetable=veg, date=today).exists():
        DailyPrice.objects.create(
            vegetable=veg,
            date=today,
            min_price=min_price,
            max_price=max_price,
            avg_price=avg_price
        )