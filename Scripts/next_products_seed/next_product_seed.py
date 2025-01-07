from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
dummy_date_dir = "../backup"
main_page_url = "https://www.morele.net/"
main_page_file = f"{dummy_date_dir}/main_page.html"
from selenium import webdriver
import os
from random import randint
import copy
import utils

# pobiera nam wszystkie kategoie
main_url = "https://www.morele.net/"
# sport and tourists
gym = [
    "https://www.morele.net/kategoria/akcesoria-do-jogi-1794/",
    "https://www.morele.net/kategoria/kettlebell-12377/",
    "https://www.morele.net/kategoria/lawki-do-cwiczen-1490/",
    "https://www.morele.net/kategoria/gryfy-i-zaciski-2946/",
    "https://www.morele.net/kategoria/hantle-1783/",
    "https://www.morele.net/kategoria/obciazenie-2947/",
    "https://www.morele.net/kategoria/rollery-i-pilki-do-masazu-1797/",
    "https://www.morele.net/kategoria/stojaki-na-silownie-1779/",
]
bikes_and_accesories = [

    "https://www.morele.net/kategoria/kaski-rowerowe-1812/",
    "https://www.morele.net/kategoria/kurtki-rowerowe-1591/",
    "https://www.morele.net/kategoria/buty-rowerowe-1849/",
    "https://www.morele.net/kategoria/skutery-elektryczne-12240/",
    "https://www.morele.net/kategoria/rowery-gorskie-1807/",
    "https://www.morele.net/kategoria/rowery-turystyczne-1808/",
    "https://www.morele.net/kategoria/zapiecia-rowerowe-12015/",
]

mountains = [
    "https://www.morele.net/kategoria/kaski-wspinaczkowe-12088/",
    "https://www.morele.net/kategoria/magnezja-i-woreczki-12081/",
    "https://www.morele.net/kategoria/raki-12098/",
    "https://www.morele.net/kategoria/czekany-12099/",
    "https://www.morele.net/kategoria/akcesoria-namiotowe-1539/",
    "https://www.morele.net/kategoria/akcesoria-turystyczne-1774/",
    "https://www.morele.net/kategoria/palniki-i-kuchenki-turystyczne-1762/",
    "https://www.morele.net/kategoria/materace-turystyczne-1765/",
    "https://www.morele.net/kategoria/meble-kempingowe-1758/"
]

# games and baby
games = [
    "https://www.morele.net/kategoria/gry-logiczne-1107/",
    "https://www.morele.net/kategoria/gry-planszowe-1111/",
    "https://www.morele.net/kategoria/gry-zrecznosciowe-1121/",
    "https://www.morele.net/kategoria/zestawy-gier-1120/",
    "https://www.morele.net/kategoria/klocki-12312/",
    "https://www.morele.net/kategoria/klocki-drewniane-1038/",
    "https://www.morele.net/kategoria/puzzle-1151/"
]
babies = [
    "https://www.morele.net/kategoria/markery-i-zakreslacze-351/",
    "https://www.morele.net/kategoria/olowki-1174/",
    "https://www.morele.net/kategoria/piorniki-739/",
    "https://www.morele.net/kategoria/tornistry-738/",
    "https://www.morele.net/kategoria/temperowki-385/"
]
#   house_and_garden_url
garden = [
    "https://www.morele.net/kategoria/akcesoria-do-opryskiwaczy-10209/",
    "https://www.morele.net/kategoria/konewki-12363/",
    "https://www.morele.net/kategoria/nawozy-10210/",
    "https://www.morele.net/kategoria/plandeki-10194/",
    "https://www.morele.net/kategoria/ziemie-i-podloza-10089/",
    "https://www.morele.net/kategoria/weze-10040/",
    "https://www.morele.net/kategoria/pompy-i-hydrofory-10376/",
    "https://www.morele.net/kategoria/grabie-12358/",
    "https://www.morele.net/kategoria/kosiarki-akumulatorowe-12366/",
    "https://www.morele.net/kategoria/kosiarki-elektryczne-12367/",
    "https://www.morele.net/kategoria/sekatory-10212/",
    "https://www.morele.net/kategoria/taczki-10323/",
    "https://www.morele.net/kategoria/traktory-ogrodowe-12342/",
    "https://www.morele.net/kategoria/zylki-i-glowice-do-podkaszarek-12376/"
]

cars = [
    "https://www.morele.net/kategoria/czujniki-i-kamery-parkowania-1735/",
    "https://www.morele.net/kategoria/kolpaki-1694/",
    "https://www.morele.net/kategoria/nawigacja-gps-139/",
    "https://www.morele.net/kategoria/pokrowce-na-siedzenia-367/",
    "https://www.morele.net/kategoria/uchwyty-na-telefon-536/",
    "https://www.morele.net/kategoria/zaglowki-podrozne-1101/",
    "https://www.morele.net/kategoria/alkomaty-403/"
]
# utils
def get_product_images(driver):
    try:
        all_images_urls = []
        time.sleep(0.5)

        # Szukamy obrazów w elementach div o klasie "swiper-slide mobx"
        images_divs = driver.find_elements(By.CSS_SELECTOR, "div.swiper-slide.mobx")
        for div in images_divs:
            sources = div.find_elements(By.CSS_SELECTOR, 'source[media="(min-width:1550px)"]')
            for source in sources:
                url = source.get_attribute("srcset")
                if url and not url.lower().endswith('.svg'):
                    all_images_urls.append({"url": url})

        # Jeśli all_images_urls jest puste, próbujemy innego selektora
        if not all_images_urls:
            images_divs = driver.find_elements(By.CSS_SELECTOR, "div.swiper-slide.mobx.swiper-slide-active")
            for div in images_divs:
                images = div.find_elements(By.TAG_NAME, "img")
                for img in images:
                    url = img.get_attribute("src") or img.get_attribute("data-src")
                    if url and not url.lower().endswith('.svg'):
                        all_images_urls.append({"url": url})

        # Jeśli nadal puste, ustawiamy domyślną wartość
        if not all_images_urls:
            all_images_urls = [{"url": "no images this time"}]

        print(all_images_urls)
        # last filtering by newslatter and not .svg extension
        filtered_images = [
            image for image in all_images_urls
            if not (".svg" in image["url"] or "newsletter" in image["url"])
        ]
        return filtered_images

    except Exception as image_exception:
        print("Exception occurred while loading photos. Let's go try with another one")
        return [{"url": "no images this time"}]

def get_product_data(driver, xpath_value, attribute_value):
    element = driver.find_element(By.XPATH, xpath_value)
    attribute_text_value = element.get_attribute(attribute_value)
    return attribute_text_value

def load_product_subcategories():
    categories_list =  driver.find_elements(By.CSS_SELECTOR, "li.breadcrumb-item.link-box")
    sub_categories_list = []
    try:
        for prd_category in categories_list:
            category_link_tag = prd_category.find_element(By.XPATH, ".//a[contains(@class, 'main-breadcrumb')]")
            category_href = category_link_tag.get_attribute("href")
            category_name = category_link_tag.find_element(By.XPATH, "./span").text
            print(category_name)
            json_pattern = {"name" : category_name, "url" : category_href}
            sub_categories_list.append(json_pattern)
    except Exception as category_load_exception:
        print(f"There occured some error while loading category : {category_load_exception}")
    return sub_categories_list

def load_links_to_products(driver, page_url):
    driver.get(page_url)
    utils.click_on_cookies_button(driver)
    links_with_title = driver.find_elements(By.XPATH, '//a[@href and @title]')
    products_links = [element.get_attribute("href") for element in links_with_title]
    current_product_links = utils.load_json_data("../next_products_seed/products_seed_links.json")
    current_product_links["products_links"].extend(products_links[:15])
    utils.write_json_data(current_product_links, "../next_products_seed/products_seed_links.json")



def load_file_product_detail(driver, product_page_url):
    driver.get(product_page_url)
    utils.click_on_cookies_button(driver)

    try:
        product_name = get_product_data(driver, xpath_value='//h1[@class="prod-name"]',
                                        attribute_value="data-default")
    except Exception as name_exception:
        print("The product doesnt exist. Go next ")
        return
    try:
        product_price = get_product_data(driver, xpath_value='//div[@class="product-price"]',
                                         attribute_value="data-default-price-gross")
    except Exception as name_exception:
        print("Setting default product price")
        product_price = f"{randint(20,300)}.99 zł"
    try:
        product_average_rate = driver.find_element(By.XPATH, '//div[@class="review-rating-number"]').text
    except Exception as e:
        print("Average not found, Setting default value.")
        product_average_rate = f"{randint(0,5)}/5"

    spec_rows = driver.find_elements(By.XPATH, '//div[@class="specification__row"]')
    product_images = get_product_images(driver)
    product_categories  = load_product_subcategories()
    product_specifications = []
    for row in spec_rows:
        try:
            name = row.find_element(By.XPATH, './span[@class="specification__name"]').text
            value = row.find_element(By.XPATH, './span[@class="specification__value"]').text
            product_specifications.append({"name": name, "value": value})
        except Exception as driver_exception:
            print(f"Error during processing driver content {driver_exception}")

    current_product_details = utils.load_json_data("../next_products_seed/products_seeded_data.json")
    new_product_details_item = {
        "product_url": product_page_url,
        "product_name": product_name,
        "product_price": product_price,
        "product_images": product_images,
        "product_average_rate": product_average_rate,
        "specifications": product_specifications,
        "product_categories" : product_categories
    }
    current_product_details['Products'].append(new_product_details_item)
    utils.write_json_data(current_product_details, "../next_products_seed/products_seeded_data.json")


driver = webdriver.Chrome()
driver.maximize_window()
def load_product_links():
    links_lists = [gym, bikes_and_accesories, mountains, games, babies, garden,cars]
    for links_urls in links_lists:
        for url in links_urls:
            load_links_to_products(driver, url)
            # load_file_product_detail(driver, url)

if __name__ == '__main__':
    #load_product_links() # to seed product links
    all_products_links = utils.load_json_data("../next_products_seed/products_seed_links.json")
    for url in all_products_links["products_links"]:
        load_file_product_detail(driver, url)
