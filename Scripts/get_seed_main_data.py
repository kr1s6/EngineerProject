import json

# Ścieżka do pliku JSON
FILE_PATH = "categories_seed.json"

def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Plik {file_path} nie został znaleziony.")
        return None
    except json.JSONDecodeError as e:
        print(f"Błąd dekodowania JSON: {e}")
        return None

def display_categories_from_file(file_path):
    data = load_json(file_path)
    print(data)
    if data and "categories" in data:
        for category in data["categories"]:
            print(f"Kategoria: {category['name']}")
            print("Podkategorie:")
            for sub_category in category.get("subcategories", []):
                print(f"  - {sub_category['name']}")
            print("-" * 40)  # Separator dla lepszej czytelności
    else:
        print("Nie znaleziono kategorii w pliku JSON lub dane są puste.")

# Wywołanie funkcji
if __name__ == "__main__":
    display_categories_from_file(FILE_PATH)
