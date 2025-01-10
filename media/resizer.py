from PIL import Image
import os

# Funkcja skalująca zdjęcia z zachowaniem proporcji
def resize_images_with_proportions(directory, width, height):
    for filename in os.listdir(directory):
        if filename.endswith('.jpg') or filename.endswith('.png'):  # Obsługuje tylko formaty JPG i PNG
            image_path = os.path.join(directory, filename)
            image = Image.open(image_path)

            # Obliczenie nowych wymiarów, zachowując proporcje
            original_width, original_height = image.size
            aspect_ratio = original_width / original_height

            if width / height > aspect_ratio:
                new_width = int(height * aspect_ratio)
                new_height = height
            else:
                new_width = width
                new_height = int(width / aspect_ratio)

            # Skalowanie obrazu z zachowaniem proporcji
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)

            # Tworzenie białego tła o wymiarach docelowych
            new_image = Image.new('RGB', (width, height), (255, 255, 255))
            new_image.paste(resized_image, ((width - new_width) // 2, (height - new_height) // 2))

            # Zapisanie przeskalowanego zdjęcia z zachowaniem proporcji
            new_image.save(image_path)

# Skalowanie zdjęć w danym katalogu
resize_images_with_proportions('./products', 1064, 1064)
