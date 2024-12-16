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
from random import randint
import copy

def get_product_images(driver):
    try:
        all_images_urls = []
        images_divs = driver.find_elements(By.CSS_SELECTOR, "div.swiper-container.swiper-gallery-thumbs.swiper-container-vertical.swiper-container-free-mode")
        for div in images_divs:
            images = div.find_elements(By.TAG_NAME, "img")
            for img in images:
                url = img.get_attribute("src") or img.get_attribute("data-src")
                if url:
                    all_images_urls.append({"url": url})

        return all_images_urls

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
        "product_url": product_page_url,
        "product_name": product_name,
        "product_price": product_price,
        "product_images": product_images,
        "product_average_rate": product_average_rate,
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

def load_product_subcategories(product):
    categories_list =  driver.find_elements(By.CSS_SELECTOR, "li.breadcrumb-item.link-box")
    sub_categories_list = []
    try:
        for prd_category in categories_list:

            category_link_tag = prd_category.find_element(By.XPATH, ".//a[contains(@class, 'main-breadcrumb')]")
            category_href = category_link_tag.get_attribute("href")
            category_name = category_link_tag.find_element(By.XPATH, "./span").text
            json_pattern = {"name" : category_name, "url" : category_href}
            sub_categories_list.append(json_pattern)
    except Exception as category_load_exception:
        print(f"There occured some error while loading category : {category_load_exception}")
    return sub_categories_list

def change_final_products_images(driver):
    products_details = utils.load_json_data("../generated_files/last_version_product_details.json")
    for product in products_details["Products"]:
        driver.get(product["product_url"])
        uploaded_new_images = get_product_images(driver)
        product["product_images"] = uploaded_new_images
        upload_last_last = utils.load_json_data("../generated_files/last_last_product_details.json")
        upload_last_last["Products"].append(product)
        utils.write_json_data(upload_last_last, "../generated_files/last_last_product_details.json")


def upload_missing_data_to_product_details(driver):
    products_details = utils.load_json_data("../generated_files/generated_products_details.json")

    flag = False
    counter = 0
    for product in products_details["Products"]:
        print(counter)
        counter += 1
        if product["product_url"] == "https://www.morele.net/ups-green-cell-600va-360w-power-proof-ups01lcd-866132/":
            flag = True
        if flag == True:
            product_copy = copy.deepcopy(product)
            # loading missing phots
            driver.get(product["product_url"])
            # check whether product len is 0 and ( contains "no image .." or ""
            if len(product["product_images"]) == 1:
                if product["product_images"][0]["url"] == "no images this time" or (product["product_images"][0]["url"] == ""):
                    uploaded_new_images = get_product_images(driver)
                    product_copy["product_images"] = uploaded_new_images

                else:
                    print("Only one photo. Phhi. Then let it stay like this")
            # check whether any of product images is empty
            elif any(image.get("url") == "" for image in product["product_images"]):
                uploaded_new_images = get_product_images(driver)
                product_copy["product_images"] = uploaded_new_images
            filtered_images = [
                image for image in product_copy["product_images"]
                if not (".svg" in image["url"] or "newsletter" in image["url"])
            ]
            product_copy["product_images"] = filtered_images
            # loading missing product_categories
            sub_categories = load_product_subcategories(product)
            product_copy["product_categories"] = sub_categories
            # setting missing average as random_value
            if product["product_average_rate"] == "0/5":
                random_new_average_value = randint(0,5)
                product_copy["product_average_rate"] = f"{random_new_average_value}/5"

            if product_copy["product_images"] == []:
                print("The PRODUCT IMAGES WENT WRONG")

            last_version_products = utils.load_json_data("../generated_files/last_version_product_details.json")
            last_version_products['Products'].append(product_copy)
            utils.write_json_data(last_version_products, "../generated_files/last_version_product_details.json")



def run_product_load(driver):
    filtered_products_links = utils.load_json_data('../generated_files/filtered_products_links.json')
    for product_category in filtered_products_links["products_links"]:
        product_links = product_category["links"]
        for link_url in product_links:
            driver.get(link_url)
            utils.click_on_cookies_button(driver)
            load_product_filter(driver, link_url)
            load_file_product_detail(driver, link_url)

if __name__ == '__main__':
    driver = webdriver.Chrome()
    # filtered_products_links = utils.load_json_data('../generated_files/filtered_products_links.json')
    # upload_missing_data_to_product_details(driver)
    change_final_products_images(driver)