from selenium.webdriver.common.by import By
import utils

dummy_date_dir = "../backup"
main_page_url = "https://www.morele.net/"
main_page_file = f"{dummy_date_dir}/main_page.html"


def load_categories_links(driver):
    driver.get("main_page_url")
    page_categories_list = driver.find_elements(By.XPATH,
                                                '//a[contains(@class, "cn-link") and contains(@class, "cn-row-menu-link-nested") and contains(@class, "cn-menu-link") and @href]'
                                                )

    category_links = [element.get_attribute("href") for element in page_categories_list]
    utils.write_variable_into_python_file("category_links", category_links)
    return category_links


def run_category_load(driver):
    utils.load_page_file(main_page_file, main_page_url, driver)
    generated_categories = utils.load_json_data("../generated_files/generated_categories.json")
    if len(generated_categories.category_links) < 1:
        categories = load_categories_links(driver)
    else:
        categories = generated_categories.category_links
    return categories
