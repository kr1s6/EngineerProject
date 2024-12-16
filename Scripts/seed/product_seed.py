from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import utils

dummy_date_dir = "../backup"
main_page_url = "https://www.morele.net/"
main_page_file = f"{dummy_date_dir}/main_page.html"
from selenium import webdriver
import os


def get_product_images(driver):
    target_element = driver.find_element(By.ID, "specification")
    target_position = target_element.location['y']

    current_position = 0
    step = 50
    attributes_urls = None
    try:
        while current_position < target_position:
            current_position += step
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(0.001)

        driver.execute_script("arguments[0].scrollIntoView(true);", target_element)

        images = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//img[contains(@class, 'lazy-desc') and contains(@class, 'loaded')]"))
        )
        attributes_urls = [{"url" : img.get_attribute("src")} for img in images]

    except Exception as image_exception:
        print(" Exception occured while loading photos. Lets go try with another one")
        attributes_urls = [{"url": "no images this time"}]

    return attributes_urls


def get_product_data(driver, xpath_value, attribute_value):
    element = driver.find_element(By.XPATH, xpath_value)
    attribute_text_value = element.get_attribute(attribute_value)
    return attribute_text_value


def load_file_product_detail(driver, product_page_url):
    driver.get(product_page_url)
    # utils.click_on_cookies_button(driver)
    spec_rows = driver.find_elements(By.XPATH, '//div[@class="specification__row"]')

    try:
        product_name = get_product_data(driver, xpath_value='//h1[@class="prod-name"]',
                                        attribute_value="data-default")

        product_price = get_product_data(driver, xpath_value='//div[@class="product-price"]',
                                         attribute_value="data-default-price-gross")
        product_average_rate = driver.find_element(By.XPATH, '//div[@class="review-rating-number"]').text
    except Exception as average_rate:
        print("Average is not present. So we are using 0")
        product_name = "Ni ma nazwy produktu. O chuj tu chodzi"
        product_price = "ni ma ceny. Sorka xD"
        product_average_rate = "0/5"
    product_images = get_product_images(driver)

    product_specifications = []

    for row in spec_rows:
        try:
            name = row.find_element(By.XPATH, './span[@class="specification__name"]').text
            value = row.find_element(By.XPATH, './span[@class="specification__value"]').text
            product_specifications.append({"name": name, "value": value})
        except Exception as driver_exception:
            print(f"Error during processing driver content {driver_exception}")

    current_product_details = utils.load_json_data("../generated_files/generated_products_details.json")
    new_product_details_item = {
        "product_url" : product_page_url,
        "product_name": product_name,
        "product_price": product_price,
        "product_images": product_images,
        "product_average_rate" : product_average_rate,
        "specifications": product_specifications
    }
    current_product_details['Products'].append(new_product_details_item)
    utils.write_json_data(current_product_details, "../generated_files/generated_products_details.json")


def check_whether_element_has_attribute(root_element, element_attribute, element_value, attribute_value):
    element = root_element.find_element(element_attribute, element_value)
    try:
        print(element.text.strip())
        if element.find_element(By.CSS_SELECTOR, attribute_value):
            element_text_value = element.text.strip()
            return element_text_value
        else:
            return None
    except Exception as driver_exception:
        print(f"There occurred an error during driver compression: {driver_exception}")
        return None


def load_product_filter(driver, product_url):
    specification_rows = driver.find_elements(By.CLASS_NAME, "specification__row")
    filters = []
    for row in specification_rows:
        try:
            specification_text_name = check_whether_element_has_attribute(
                row,
                By.CLASS_NAME,
                "specification__name",
                "a[data-rate-to='fhead']"
            )
            if specification_text_name is not None:
                specification_text_value = row.find_element(By.CLASS_NAME, "specification__value")
                text_value = specification_text_value.text.strip()
                filters.append({"name": specification_text_name, "value": text_value})
            else:
                potential_attributes_value = ["a[data-rate-to='fvalue']", "a[target='_blank']"]
                for attribute_value in potential_attributes_value:
                    potential_correct_attribute_value = check_whether_element_has_attribute(
                        row,
                        By.CLASS_NAME,
                        "specification__value ",
                        attribute_value
                    )
                    if potential_correct_attribute_value is not None:
                        specification_text_value = potential_correct_attribute_value
                        specification_text_name = row.find_element(By.CLASS_NAME, "specification__name")
                        text_name = specification_text_name.text.strip()
                        filters.append({"name": text_name, "value": specification_text_value})
                    else:
                        continue

        except Exception as driver_exception:
            print(f"Error occurred during processes driver content: {driver_exception}")
            continue
    new_product_filters = {
        "url": product_url,
        "filters": filters
    }
    current_products = utils.load_json_data("../generated_files/generated_product_filters.json")
    current_products['products'].append(new_product_filters)
    utils.write_json_data(current_products, "../generated_files/generated_product_filters.json")


def run_product_load(driver):
    pass
    # extracted_categories = categories_seed.run_category_load(driver)
    # counter = 0
    # for category_page_url in extracted_categories:
    #     links_seed.load_links_to_products(driver, category_page_url, counter)
    #     counter += 1
    #     time.sleep(1)


if __name__ == '__main__':
    driver = webdriver.Chrome()
    filtered_products_links = utils.load_json_data('../generated_files/filtered_products_links.json')
    for product_category in filtered_products_links["products_links"]:
        product_links = product_category["links"]
        for link_url in product_links:
            # driver.get(link_url)
            # utils.click_on_cookies_button(driver)
            # load_product_filter(driver, link_url)
            load_file_product_detail(driver, link_url)
