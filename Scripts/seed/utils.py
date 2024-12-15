import ast
import selenium
import time
from selenium.webdriver.common.action_chains import ActionChains
import json
import os
import re


def get_list_variables(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())

    list_variables: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value, ast.List):
                    list_variables.append(target.id)

    return list(set(list_variables))  # unique variables


def write_variable_into_python_file(update_var, update_value, seed_file_path="generated_products_links.py"):
    with open(seed_file_path, "a", encoding="utf-8") as file:
        file.write(f"{update_var} = {update_value}")


def write_json_data(json_data, json_path):
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)


def load_json_data(json_path):
    with open(json_path, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    return json_data


def convert_python_variables_to_json(file_path, var):
    json_data = json.dumps(var, indent=4)
    with open(file_path, "w", encoding="utf-8") as json_file:
        json_file.write(json_data)


def click_on_cookies_button(driver):
    try:
        time.sleep(2)
        accept_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Akceptuję wszystko')]")
        ActionChains(driver).move_to_element(accept_button).click(accept_button).perform()
    except Exception as e:
        print(f"There occures some error {e}")


def load_page_file(driver, file_path: str, page_url):
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


def extract_pattern(url):
    pattern = r'https://www\.morele\.net/([a-zA-Z0-9]+)'
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    return None
