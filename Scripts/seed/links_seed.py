from selenium.webdriver.common.by import By

import json
import utils

dummy_date_dir = "../backup"
main_page_url = "https://www.morele.net/"
main_page_file = f"{dummy_date_dir}/main_page.html"


def load_links_to_products(driver, page_url, amount):
    driver.get(page_url)
    utils.click_on_cookies_button(driver)
    links_with_title = driver.find_elements(By.XPATH, '//a[@href and @title]')
    products_links = [element.get_attribute("href") for element in links_with_title]
    utils.write_variable_into_python_file(f"products_links{amount}", products_links)


def group_links_patterns():
    grouped_patterns = list()
    generated_products_links = utils.load_json_data("../generated_files/generated_products_links.json")
    for link_url in generated_products_links.products_links:
        matched_regex = utils.extract_pattern(link_url)
        new_url = f"{main_page_url}{matched_regex}"
        if new_url not in grouped_patterns:
            grouped_patterns.append(new_url)

    utils.convert_python_variables_to_json(file_path="../generated_files/generated_product_patterns.json",
                                           var=grouped_patterns)


def reduce_amount_of_products_links_based_on_pattern(grouped_paterns: list[str], treshold):
    generated_products_links = utils.load_json_data("../generated_files/generated_products_links.json")
    products_links = []
    # take generated_patterns and based on them create 15 product links
    for pattern in grouped_paterns:
        matching_links = [link for link in generated_products_links if link.startswith(pattern)]
        if matching_links:
            products_links.append({
                "name": utils.extract_pattern(pattern),
                "links": matching_links[:treshold]  # Weź tylko pierwsze 15 linków
            })
    # if products amount is less than 10 we remote it
    filtered_result = {
        "products_links": [
            product for product in products_links
            if len(product['links']) >= 10
        ]
    }
    with open('../generated_files/filtered_products_links.json', 'w', encoding='utf-8') as json_file:
        json.dump(filtered_result, json_file, indent=4, ensure_ascii=False)


def run_links_load(driver):
    pass
