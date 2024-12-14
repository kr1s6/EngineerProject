from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import utils
import categories_seed
import links_seed

dummy_date_dir = "../dummy_data"
main_page_url = "https://www.morele.net/"
main_page_file = f"{dummy_date_dir}/main_page.html"


def get_product_images(driver):
    target_element = driver.find_element(By.ID, "specification")
    target_position = target_element.location['y']

    current_position = 0
    step = 50

    while current_position < target_position:
        current_position += step
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(0.05)

    driver.execute_script("arguments[0].scrollIntoView(true);", target_element)

    images = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//img[contains(@class, 'lazy-desc') and contains(@class, 'loaded')]"))
    )
    attributes_urls = [img.get_attribute("src") for img in images]
    return {"product_images": attributes_urls}


def get_product_data(driver, xpath_value, attribute_value, specification_key):
    element = driver.find_element(By.XPATH, xpath_value)
    attribute_text_value = element.get_attribute(attribute_value)
    return {specification_key: attribute_text_value}


def get_product_filter(driver):
    specification_rows = driver.find_elements(By.CLASS_NAME, "specification__row")
    filters = []
    for row in specification_rows:
        try:
            name_element = row.find_element(By.CLASS_NAME, "specification__name")
            name = name_element.text.strip()
            value_elements = row.find_elements(By.CSS_SELECTOR, ".specification__value a[data-rate-to='fvalue']")
            for value_element in value_elements:
                value = value_element.text.strip()
                filters.append({"name": name, "value": value})
        except Exception as e:
            continue

    result = {"filters": filters}


def load_file_product_detail(driver, produt_page_url, counter):
    driver.get(produt_page_url)
    utils.click_on_cookies_button(driver)
    spec_rows = driver.find_elements(By.XPATH, '//div[@class="specification__row"]')
    product_name = get_product_data(xpath_value='//h1[@class="prod-name"]',
                                    attribute_value="data-default",
                                    specification_key="product_name")
    product_price = get_product_data(xpath_value='//div[@class="product-price"]',
                                     attribute_value="data-default-price-gross",
                                     specification_key="product_price")
    try:
        product_average_rate = driver.find_element(By.XPATH, '//div[@class="review-rating-number"]').text
    except Exception as average_rate:
        print("Average is not present. So we are using 0")
        product_average_rate = "0/5"
    product_images = get_product_images()

    specification_data = [product_name, product_price,
                          product_images,
                          {"product_average_rate": product_average_rate}]

    for row in spec_rows:
        try:
            name = row.find_element(By.XPATH, './span[@class="specification__name"]').text
            value = row.find_element(By.XPATH, './span[@class="specification__value"]').text
            specification_data.append({"name": name, "value": value})
        except Exception as e:
            print(f"Błąd podczas przetwarzania: {e}")

    utils.write_variable_into_python_file(f"products_details{counter}", specification_data,
                                          "../generated_files/generated_product_details.py")



def run_product_load(driver):
    extracted_categories = categories_seed.run_category_load(driver)
    counter = 0
    for category_page_url in extracted_categories:
        links_seed.load_links_to_products(driver, category_page_url, counter)
        counter += 1
        time.sleep(1)
