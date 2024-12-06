import os
from importlib.metadata import files

import requests
from bs4 import BeautifulSoup


class ProductImageGenerator():
    """
       A class to download images based on a product name by searching online.
   """
    def __init__(self, product, download_path = "../media/products", ):
        self.download_path = download_path
        self.product = product
        
    def download_image(self, url, file_path):
        """
           Download an image from the provided URL and save it to the disk.
               :param url: The URL of the image to download.
               :param file_path: File path which will be saves image
       """
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Pobrano: {file_path}")
        else:
            print(f"Nie udało się pobrać: {url}")

    def search_and_download(self, file_path):
        """
        Search for an image of the class given product name on Google and download it.
          """
        os.makedirs(self.download_path, exist_ok=True)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        search_query = self.product.replace(" ", "+")
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
                image_name = self.download_image(src, file_path)
                break

"""
    Example of use:
        example_product = "Apple iPhone 14 Pro Max"
        print(f"Wyszukiwanie dla: {example_product}")
        generator = ProductImageGenerator(product=example_product)
        generator.search_and_download()
"""
