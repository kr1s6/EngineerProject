from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import utils
import categories_seed
import links_seed

dummy_date_dir = "../backup"
main_page_url = "https://www.morele.net/"
main_page_file = f"{dummy_date_dir}/main_page.html"
import seed_runer

from selenium import webdriver


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


def load_file_product_detail(driver, product_page_url, counter):
    driver.get(product_page_url)
    utils.click_on_cookies_button(driver)
    spec_rows = driver.find_elements(By.XPATH, '//div[@class="specification__row"]')
    product_name = get_product_data(driver, xpath_value='//h1[@class="prod-name"]',
                                    attribute_value="data-default",
                                    specification_key="product_name")
    product_price = get_product_data(driver, xpath_value='//div[@class="product-price"]',
                                     attribute_value="data-default-price-gross",
                                     specification_key="product_price")
    try:
        product_average_rate = driver.find_element(By.XPATH, '//div[@class="review-rating-number"]').text
    except Exception as average_rate:
        print("Average is not present. So we are using 0")
        product_average_rate = "0/5"
    product_images = get_product_images(driver)

    specification_data = [product_name, product_price,
                          product_images,
                          {"product_average_rate": product_average_rate}]

    for row in spec_rows:
        try:
            name = row.find_element(By.XPATH, './span[@class="specification__name"]').text
            value = row.find_element(By.XPATH, './span[@class="specification__value"]').text
            specification_data.append({"name": name, "value": value})
        except Exception as driver_exception:
            print(f"Error during processing driver content {driver_exception}")

    utils.write_variable_into_python_file(f"products_details{counter}", specification_data,
                                          "../backup/generated_product_details.py")


def check_whether_element_has_attribute(element_attribute, element_value, attribute_value):
    element = driver.find_element(element_attribute, element_value)
    try:
        if element.find_elements(By.CSS_SELECTOR, attribute_value):
            element_text_value = element.text.strip()
            return element_text_value
        else:
            return None
    except Exception as driver_exception:
        print(f"There occurred an error during driver compression: {driver_exception}")


def get_product_filter(driver):
    specification_rows = driver.find_elements(By.CLASS_NAME, "specification__row")
    filters = []
    for row in specification_rows:
        try:
            specification_text_name = check_whether_element_has_attribute(
                By.CLASS_NAME, "specification__name", "a[data-rate-to='fvalue']"
            )
            specification_text_value =  check_whether_element_has_attribute(
                By.CLASS_NAME, "specification__value ", "a[data-rate-to='fvalue']"
            )
            if specification_text_value is not None or specification_text_name is not None:
                for value_element in value_elements:
                    value = value_element.text.strip()
                    filters.append({"name": name, "value": value})

        except Exception as driver_exception:
            print(f"Error occurred during processes driver content: {driver_exception}")
            continue
    result = {"filters": filters}
    print(result)


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
            driver.get(link_url)
            utils.click_on_cookies_button(driver)
            get_product_filter(driver)
