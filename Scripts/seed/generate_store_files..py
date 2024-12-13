from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import os.path
import seeded_detail_data

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
    return categories


def write_variable_into_python_file(update_var, update_value):
    with open("seeded_detail_data.py", "a") as file:
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
    products_links = [ element.get_attribute("href") for element in links_with_title]
    write_variable_into_python_file(f"products_links{amount}", products_links)


def load_file_product_detail(produt_page_url):
    driver.get(produt_page_url)
    html_Content = driver.page_source
    click_on_cookies_button()


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
    load_file_product_detail(product_link[0])



driver.quit()

