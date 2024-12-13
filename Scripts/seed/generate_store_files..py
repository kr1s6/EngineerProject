from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import os.path
import seeded_detail_data
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Chrome()
dummy_date_dir = "../dummy_data"


def click_on_cookies_button():
    try:
        time.sleep(2)
        accept_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Akceptuję wszystko')]")
        ActionChains(driver).move_to_element(accept_button).click(accept_button).perform()
    except Exception as e:
        print(f"There occures some error {e}")


def load_categories_links():
    driver.get("file:///C:/Users/Czes%C5%82aw/Desktop/Repositories/EngineerProject/Scripts/dummy_data/main_page.html")
    html_content = driver.page_source
    page_categories_list = driver.find_elements(By.XPATH,
                                                '//a[contains(@class, "cn-link") and contains(@class, "cn-row-menu-link-nested") and contains(@class, "cn-menu-link") and @href]')

    category_links = [element.get_attribute("href") for element in page_categories_list]
    write_variable_into_python_file("category_links", category_links)
    return category_links


def write_variable_into_python_file(update_var, update_value, seed_file_path="seeded_detail_data.py"):
    with open(seed_file_path, "a", encoding="utf-8") as file:
        file.write(f"{update_var} = {update_value}")


def load_page_file(file_path: str, page_url):
    if not os.path.isfile(file_path):
        driver.get(page_url)
        html_content = driver.page_source
        click_on_cookies_button()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Page content has been saved in file main_page.html.")
        driver.quit()
    else:
        print("File already created")


def load_links_to_products(page_url, amount):
    driver.get(page_url)
    html_content = driver.page_source
    click_on_cookies_button()
    links_with_title = driver.find_elements(By.XPATH, '//a[@href and @title]')
    products_links = [element.get_attribute("href") for element in links_with_title]
    write_variable_into_python_file(f"products_links{amount}", products_links)


def get_product_images():
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
            EC.presence_of_all_elements_located((By.XPATH, "//img[contains(@class, 'lazy-desc') and contains(@class, 'loaded')]"))
        )
    attributes_urls = [img.get_attribute("src") for img in images]
    return {"product_images": attributes_urls}

def get_product_data(xpath_value, attribute_value, specification_key):
    element = driver.find_element(By.XPATH, xpath_value)
    attribute_text_value = element.get_attribute(attribute_value)
    return {specification_key: attribute_text_value}


def load_file_product_detail(produt_page_url, counter):
    driver.get(produt_page_url)
    html_content = driver.page_source
    html_content = html_content.encode('utf-8').decode('utf-8')
    click_on_cookies_button()
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

    write_variable_into_python_file(f"products_details{counter}", specification_data, "generated_product_details.py")


if __name__ == '__main__':
    main_page_url = "https://www.morele.net/"
    # load_page_file(f"{dummy_date_dir}/main_page.html", main_page_url)
    # if len(seeded_detail_data.category_links) < 1:
    #     categories = load_categories_links()
    # else:
    # extracted_categories = seeded_detail_data.category_links
    # counter = 0
    # for category_page_url in extracted_categories:
    #     load_links_to_products(category_page_url,counter)
    #     counter += 1
    #     time.sleep(1)
    product_link = seeded_detail_data.products_links0
    load_page_file(f"{dummy_date_dir}/main_page.html", product_link[0])
    for product_index in range(0, 10):
        load_file_product_detail(product_link[product_index], product_index)

driver.quit()
