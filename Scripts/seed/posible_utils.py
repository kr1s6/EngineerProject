import ast


def get_list_variables(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())

    list_variables: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value, ast.List):
                    list_variables.append(target.id)

    return list(set(list_variables))  # unique variables
import re
import json
from collections import defaultdict

# Lista linków
links = [
    "https://www.morele.net/laptop-gigabyte-g6x-9kg-2024-i7-13650hx-16-gb-1-tb-rtx-4060-165-hz-9kg-43ee854sd-13179206/",
    "https://www.morele.net/laptop-msi-thin-15-b12ucx-1818xpl-i5-12450h-16-gb-512-gb-rtx-2050-144-hz-13354141/",
    "https://www.morele.net/laptop-gigabyte-aorus-16x-9kg-2024-i7-13650hx-16-gb-1-tb-rtx-4060-165-hz-9kg-43eec54sd-14202658/",
    "https://www.morele.net/laptop-lenovo-legion-pro-5-16irx9-i5-14500hx-32-gb-1-tb-rtx-4060-240-hz-83df00ekpb-13219116/",
    "https://www.morele.net/glosniki-komputerowe-creative-gigaworks-t20-series-ii-2-0-51mf1610aa000-146607/",
    "https://www.morele.net/glosniki-komputerowe-logitech-z333-20w-980-001202-172810/",
    "https://www.morele.net/laptop-asus-tuf-gaming-a16-advantage-edition-r7-7735hs-16-gb-512-gb-rx-7600s-144-hz-fa617xu-ns76-13219116/",
    "https://www.morele.net/glosniki-komputerowe-genius-sp-hf1800a-60w-31730922100-111124/",
    "https://www.morele.net/laptop-acer-nitro-5-an515-58-i7-12700h-16-gb-1-tb-rtx-3070-ti-an515-58-504z-14202658/",
    "https://www.morele.net/glosniki-przenosne-jbl-charge-5-12345/",
    "https://www.morele.net/glosniki-przenosne-sony-srs-xb43-67890/",
    "https://www.morele.net/laptop-hp-victus-16-e1086nw-r7-6800h-16-gb-512-gb-rtx-3050-ti-146607/",
    "https://www.morele.net/glosniki-komputerowe-creative-inspire-t10-51mf1600aa000-111124/"
]

# Funkcja do ekstrakcji głównego wzorca z linku
def extract_pattern(url):
    match = re.match(r'https://www\.morele\.net/([a-zA-Z0-9-]+(?:-[a-zA-Z0-9-]+)?)', url)
    if match:
        return match.group(1)
    return None

# Grupowanie linków według wzorców
grouped_links = defaultdict(list)
for link in links:
    pattern = extract_pattern(link)
    if pattern:
        grouped_links[pattern].append(link)

# Ogranicz liczbę linków dla każdego wzorca do maksymalnie 15
threshold = 15
result = {
    "products_links": [
        {
            "name": pattern,
            "links": links[:threshold]
        }
        for pattern, links in grouped_links.items()
    ]
}

# Zapisz wynik do pliku JSON
output_path = '/mnt/data/products_links.json'
with open(output_path, 'w', encoding='utf-8') as json_file:
    json.dump(result, json_file, indent=4, ensure_ascii=False)

# Wyświetl ścieżkę do pliku JSON
output_path