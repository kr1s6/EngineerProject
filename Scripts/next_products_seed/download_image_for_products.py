import os
import sys
import requests
from django.core.files import File
from django.conf import settings
from tempfile import NamedTemporaryFile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ustawienie DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engineerProject.settings')
import django
django.setup()

from webStore.models import Product

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Sprawdza, czy żądanie się powiodło
        return response
    except requests.RequestException as e:
        print(f"Błąd pobierania obrazu: {e}")
        return None

def save_product_image(product, image_url):
    image_response = download_image(image_url)
    if image_response:
        # Utwórz tymczasowy plik z trybem w+b (zapis i odczyt)
        img_temp = NamedTemporaryFile(suffix='.jpg', mode='w+b', delete=False)
        img_temp.write(image_response.content)
        img_temp.flush()
        img_temp.seek(0)  # Przesuń wskaźnik na początek pliku po zapisaniu danych

        # Ustawienie nazwy pliku
        image_name = os.path.basename(image_url)
        product.image.save(image_name, File(img_temp), save=True)
        img_temp.close()  # Zamknij plik po zapisaniu

# Przejdź przez wszystkie produkty i ustaw pole image
products = Product.objects.all()
for product in products:
    if product.product_images_links and product.product_images_links != "no images this time":
        # Wybierz pierwszy link z listy
        first_url = product.product_images_links[0]
        if first_url:
            save_product_image(product, first_url)
    else:
        product.image = 'products/default_product.png'
        product.save()
    print(f"Image created: for product {product.name}")


print("Zaktualizowano pole image dla produktów.")
