import json
import os
import sys
import django
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ustawienie DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineerProject.settings')
django.setup()


from webStore.models import Product

# Wczytaj dane z pliku JSON
with open('test.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


# Funkcja do przetwarzania ceny
def parse_price(price_str):
    return Decimal(price_str.replace(' zł', '').replace(',', '.').replace(' ', ''))


# Przetwórz dane i utwórz obiekty Product
for item in data['Products']:
    if "ni ma ceny. Sorka xD" not in item['product_price']:
        name = item['product_name']
        price = parse_price(item['product_price'])
        average_rate = Decimal(item['product_average_rate'].split('/')[0])
        product_images_links = [img['url'] for img in item['product_images']]
        product_details = {spec['name']: spec['value'] for spec in item['specifications']}
        brand = None
        for spec in item['specifications']:
            if spec['name'] == 'Producent':
                brand = spec['value']
                break

        # Utwórz i zapisz obiekt Product
        product = Product(
            name=name,
            price=price,
            average_rate=average_rate,
            product_images_links=product_images_links,
            product_details=product_details,
            brand=brand
        )
        product.save()

print("Utworzono obiekty Product.")