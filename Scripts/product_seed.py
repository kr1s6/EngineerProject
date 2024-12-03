import os
import sys
import json
from django.core.wsgi import get_wsgi_application

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineerProject.settings')

application = get_wsgi_application()

from webStore.models import Category, Product

def load_seed_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    categories_map = {}
    for category_data in data['categories']:
        category, _ = Category.objects.get_or_create(
            name=category_data['name'],
            description=category_data['description']
        )
        categories_map[category_data['name']] = category

        for subcategory_data in category_data.get('subcategories', []):
            subcategory, _ = Category.objects.get_or_create(
                name=subcategory_data['name'],
                description=subcategory_data['description']
            )
            category.subcategories.add(subcategory)
            categories_map[subcategory_data['name']] = subcategory

    for product_data in data['products']:
        product, _ = Product.objects.get_or_create(
            name=product_data['name'],
            brand=product_data['brand'],
            image=product_data['image'],
            description=product_data['description'],
            price=product_data['price'],
            average_rate=product_data['average_rate']
        )
        for category_name in product_data['categories']:
            if category_name in categories_map:
                product.categories.add(categories_map[category_name])

    print("Seed data successfully loaded!")

if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), 'seed.json')
    load_seed_data(file_path)
