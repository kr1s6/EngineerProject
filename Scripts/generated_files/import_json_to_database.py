import json
import os
import sys
import django
from decimal import Decimal
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ustawienie DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineerProject.settings')
django.setup()


from webStore.models import Product, Category
Product.objects.all().delete()
Category.objects.all().delete()

# Wczytaj dane z pliku JSON
with open('last_last_product_details.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


# Funkcja do przetwarzania ceny
def parse_price(price_str):
    return Decimal(price_str.replace(' zł', '').replace(',', '.').replace(' ', ''))


def get_or_create_category_hierarchy(categories):
    parent = None
    for cat_data in categories:
        category, created = Category.objects.get_or_create(name=cat_data['name'])
        if parent:
            category.parent.add(parent)
        parent = category
    return parent

# Przetwórz dane i utwórz obiekty Product
for item in data['Products']:
    if "there are no price" not in item['product_price']:
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

        # Obsługa kategorii
        if 'product_categories' in item:
            product_categories = item['product_categories']
            last_category = get_or_create_category_hierarchy(product_categories)
            if last_category:
                product.categories.add(last_category)  # Zakładając, że Product ma pole category
                product.save()
        print(f"Product: {product.name} created successfully")


print("Utworzono obiekty Product i przypisano kategorie.")
subprocess.run([sys.executable, 'download_image_for_products.py'])
