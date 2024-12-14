# import os
# import sys
# import json
# from django.core.wsgi import get_wsgi_application
#
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineerProject.settings')
#
# application = get_wsgi_application()
#
# from webStore.models import Category, Product
#
#
# def load_category_data(category_file, category_name):
#     file_path = os.path.join(os.path.dirname(__file__), '../CategoriesProducts', category_file)
#     with open(file_path, 'r') as file:
#         data = json.load(file)
#
#     main_category, _ = Category.objects.get_or_create(
#         name=category_name
#     )
#
#     for sub_category_data in data['sub_categories']:
#         sub_category_name = sub_category_data['sub_category_name']
#
#         sub_category, _ = Category.objects.get_or_create(
#             name=sub_category_name,
#         )
#         main_category.subcategories.add(sub_category)
#
#         for product_data in sub_category_data['products']:
#             product, _ = Product.objects.get_or_create(
#                 name=product_data['name'],
#                 brand=product_data['brand'],
#                 image=product_data['image'],
#                 description=product_data['description'],
#                 price=product_data['price'],
#                 average_rate=product_data['average_rate']
#             )
#             product.categories.add(sub_category)
#
#     print(f"Data for category '{category_name}' successfully loaded!")
#
#
# if __name__ == "__main__":
#     categories_data = generate_category_data("seed/categories_seed.json", "CategoriesProducts")
#     print(json.dumps(categories_data, indent=4, ensure_ascii=False))
#     for data in categories_data:
#         load_category_data(data["category_file"], data["category_name"])
