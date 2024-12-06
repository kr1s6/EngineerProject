import os
import json
import re

# Katalog, gdzie znajdują się pliki kategorii
CATEGORIES_DIR = "CategoriesProducts"
CATEGORIES_JSON = "categories_seed.json"

def load_categories_from_json(file_path):
    """
    Load categories and their names from the main JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return [category['name'] for category in data.get("categories", [])]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading categories from {file_path}: {e}")
        return []

def match_category_to_file(category_name, directory):
    """
    Match a category name to a JSON file in the directory using keywords or regex.
    """
    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):
            # Dopasowanie na podstawie nazwy pliku i słów kluczowych
            if re.search(re.escape(category_name).replace(" ", "_"), file_name, re.IGNORECASE):
                return file_name
    return None

def generate_category_data(json_file, directory):
    """
    Generate a list of categories with corresponding JSON files.
    """
    categories = load_categories_from_json(json_file)
    category_data = []

    for category_name in categories:
        matched_file = match_category_to_file(category_name, directory)
        if matched_file:
            category_data.append({
                "category_name": category_name,
                "category_file": matched_file
            })
        else:
            print(f"No matching file found for category: {category_name}")

    return category_data

if __name__ == "__main__":
    categories_data = generate_category_data(CATEGORIES_JSON, CATEGORIES_DIR)

    # Wyświetlenie wyników w pożądanym formacie
    print(json.dumps(categories_data, indent=4, ensure_ascii=False))
