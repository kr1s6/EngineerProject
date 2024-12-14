from selenium import webdriver
import links_seed
import categories_seed
import product_seed

driver = webdriver.Chrome()
dummy_date_dir = "../backup"
main_page_url = "https://www.morele.net/"
main_page_file = f"{dummy_date_dir}/main_page.html"

if __name__ == '__main__':
    links_seed.run_links_load(driver)
    categories_seed.run_category_load(driver)
    product_seed.run_product_load(driver)
