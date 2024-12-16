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

def get_longest_url(urls):
    if not urls:
        return None
    # Znajdź URL z największą długością
    return max(urls, key=len)

# Przejdź przez wszystkie produkty i ustaw pole image
products = Product.objects.all()
for product in products:
    if "no images this time" not in product.product_images_links:
        # Wybierz najdłuższy link z listy
        longest_url = get_longest_url(product.product_images_links)
        if longest_url:
            save_product_image(product, longest_url)
    else:
        product.image = 'products/default_product.png'
        product.save()

print("Zaktualizowano pole image dla produktów.")
