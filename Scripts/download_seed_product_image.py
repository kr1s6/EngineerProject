import os
import requests
from bs4 import BeautifulSoup



DOWNLOAD_PATH = "../media/products/"


def download_image(url, file_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Pobrano: {file_path}")
    else:
        print(f"Nie udało się pobrać: {url}")

def search_and_download(product_name):
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    search_query = product_name.replace(" ", "+")
    url = f"https://www.google.com/search?tbm=isch&q={search_query}"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Nie udało się połączyć z Google: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    images = soup.find_all("img")

    for index, img in enumerate(images):
        src = img.get("src")
        if src and src.startswith("http"):
            # Pobierz pierwszy obraz
            file_name = f"{product_name.replace(' ', '_')}_{index + 1}.jpg"
            file_path = os.path.join(DOWNLOAD_PATH, file_name)
            download_image(src, file_path)
            break  # Pobierz tylko jeden obraz

if __name__ == "__main__":
    product_names = [
        "Apple iPhone 14 Pro Max",
        "Samsung Galaxy S23 Ultra",
        "Sony WH-1000XM5 Headphones",
        "Dell XPS 15 Laptop",
        "Dyson V15 Detect Vacuum Cleaner",
        "Nintendo Switch OLED",
        "Canon EOS R6 Camera",
        "Logitech MX Master 3S Mouse",
        "Google Pixel 7 Pro",
        "PlayStation 5 Consol"
    ]

    for product in product_names:
        print(f"Wyszukiwanie dla: {product}")
        search_and_download(product)
