import time
from selenium import webdriver
from selenium_stealth import stealth  # Очень помогает для обхода блокировок на сайтах
from selenium.webdriver.chrome.service import Service  # новый вид записи driver
from selenium.webdriver.common.by import By  # новый вид записи find_element

from datetime import datetime
import requests
from bs4 import BeautifulSoup
import schedule


url = 'https://leroymerlin.kz/catalogue/stroymaterialy/'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.160 YaBrowser/22.5.4.904 Yowser/2.5 Safari/537.36"
}


def get_data():
    req = requests.get(url=url, headers=headers)
    req.encoding = 'UTF8'
    src = req.text
    soup = BeautifulSoup(src, 'lxml')

    # Сбор всех каталогов
    dict_categories = []

    categories_url_a_one_page = soup.find('ul', class_='catalog-category-page__subcategories-list')\
        .find_all('li', class_='catalog-category-page__subcategories-item subcategory')
    for url_li_one in categories_url_a_one_page:
        url_a_one = f"https://leroymerlin.kz{url_li_one.find('div', class_='subcategory__head-wrapper').find('a').get('href')}"
        dict_categories.append(url_a_one)

    categories = soup.find('ul', class_='catalog-category-page__categories-list category-list').find_all('li')
    del categories[0]

    for categories_url_li in categories:
        categories_url_a = f"https://leroymerlin.kz{categories_url_li.find('a').get('href')}"
        req1 = requests.get(url=categories_url_a, headers=headers)
        req1.encoding = 'UTF8'
        src1 = req1.text
        soup1 = BeautifulSoup(src1, 'lxml')

        categories_url_a = soup1.find('ul', class_='catalog-category-page__subcategories-list')\
            .find_all('li', class_='catalog-category-page__subcategories-item subcategory')
        for url_li_one in categories_url_a:
            url_a_one = f"https://leroymerlin.kz{url_li_one.find('div', class_='subcategory__head-wrapper').find('a').get('href')}"
            dict_categories.append(url_a_one)

    # Сбор всех карточек товарами из каждого каталога
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
    # Путь для хром бета
    options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    # Сделать в полный экран
    options.add_argument("--start-maximized")
    # Отключение Webdriver
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_argument('--no-sandbox')
    options.add_argument('enable-automation')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")

    # Фоновый режим
    # options.add_argument('--headless')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # selenium-stealth
    options.add_experimental_option('useAutomationExtension', False)  # selenium-stealth

    service = Service(executable_path="109.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url='https://www.google.com/')

    # selenium-stealth
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True
            )

    url_products = []
    count_catalog = 0
    while len(dict_categories) != 0:
        try:
            print(len(dict_categories))
            print(dict_categories[0])
            count_catalog += 1

            driver.get(f"{dict_categories[0]}")

            time.sleep(0.25)
            all_product_page_p = driver.find_element(By.XPATH, '//*[@id="vue-app"]/section[1]/div/div/div[2]/section/div[1]/div[2]/div[2]/div[1]')
            all_product_page_p.click()

            time.sleep(0.25)
            all_product_page = driver.find_element(By.XPATH, '//*[@id="sorting-quantity-order"]/option[4]')
            all_product_page.click()

            time.sleep(0.5)
            finish_url_product = []
            url_product_page = driver.find_elements(By.XPATH, '//*[@id="vue-app"]/section[1]/div/div/div[2]/section/ul/li')
            for i in url_product_page:
                url_product = i.find_element(By.CLASS_NAME, 'catalog__desc') \
                    .find_element(By.CLASS_NAME, 'catalog__desc-text') \
                    .find_element(By.CLASS_NAME, 'catalog__desc-text-wrap') \
                    .find_element(By.TAG_NAME, 'a').get_attribute('href')
                finish_url_product.append(url_product)
            while len(finish_url_product) != 0:
                try:
                    print(len(finish_url_product))
                    print(finish_url_product[0])

                    driver.get(f"{finish_url_product[0]}")
                    # time.sleep(0.5)
                    name = driver.find_element(By.XPATH, '//*[@id="vue-app"]/section[1]/div/div/div')\
                        .find_element(By.CLASS_NAME, 'product').find_element(By.CLASS_NAME, 'product__hl').text

                    price = driver.find_element(By.XPATH, '//*[@id="vue-app"]/section[1]/div/div/div')\
                        .find_element(By.CLASS_NAME, 'product') \
                        .find_elements(By.CLASS_NAME, 'product__col')[-1] \
                        .find_element(By.CLASS_NAME, 'product__price   ')\
                        .text.replace(' тг./шт.', '').replace(' тг./уп.', '').replace(' тг./м', '').replace(' ', '')

                    count_products = driver.find_element(By.XPATH, '//*[@id="vue-app"]/section[1]/div/div/div') \
                        .find_element(By.CLASS_NAME, 'product') \
                        .find_elements(By.CLASS_NAME, 'product__col')[-1] \
                        .find_element(By.CLASS_NAME, 'product__row') \
                        .find_element(By.CLASS_NAME, 'product__spinner-form').text.replace('В наличии: ', '')

                    article = driver.find_element(By.XPATH, '//*[@id="vue-app"]/section[1]/div/div/div')\
                        .find_element(By.CLASS_NAME, 'product')\
                        .find_element(By.CLASS_NAME, 'product__article').text.replace('(Артикул: ', '')[:-1]

                    if len(driver.find_elements(By.XPATH, '//*[@id="sp-product-reviews-widget"]')) == 1:
                        if len(driver.find_element(By.XPATH, '//*[@id="sp-product-reviews-widget"]').find_elements(By.CLASS_NAME, 'sp-summary')) == 1:
                            count_review = driver.find_element(By.XPATH, '//*[@id="sp-product-reviews-widget"]')\
                                .find_element(By.CLASS_NAME, 'sp-summary') \
                                .find_element(By.CLASS_NAME, 'sp-summary-rating-description') \
                                .find_element(By.TAG_NAME, 'span').text
                        else:
                            count_review = '0'
                    else:
                        count_review = '0'

                    categories_all = driver.find_elements(By.XPATH, '//*[@id="vue-app"]/section[1]/div/div/ul/li')
                    categories = f'{categories_all[2].text}/{categories_all[-1].text}'

                    print(f'{name} - {price} - {count_products} - {count_review} - {article} - {categories} - {finish_url_product[0]}')

                    del finish_url_product[0]
                    # time.sleep(0.5)

                except Exception as ex: # 27 каталог много ошибок
                    print(ex)
                    print(f'Ошибка в товаре: {finish_url_product[0]}')
                    del finish_url_product[0]
                    time.sleep(0.5)
                    continue

            del dict_categories[0]
            time.sleep(0.5)
            print(f'{count_catalog} каталог готов!')

        except Exception as ex:
            print(ex)
            print(f'Ошибка в каталога: {dict_categories[0]}')
            del dict_categories[0]
            time.sleep(0.5)
            continue

    driver.close()
    driver.quit()

    print(len(url_products))
    print(len(list(set(url_products))))


# def google_table(dict_cards):
#     import os.path
#
#     from googleapiclient.discovery import build
#     from googleapiclient.errors import HttpError
#     from google.oauth2 import service_account
#
#     SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
#
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
#
#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#
#     # mail bot 'parsers@parsers-372008.iam.gserviceaccount.com'
#     SAMPLE_SPREADSHEET_ID = '107SdHe8_dV6npe_dKE-7xA2QJgxz6ZOywOy-GZyrZX0'
#     SAMPLE_RANGE_NAME = 'micom.kz!A1:D'
#
#     try:
#         service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()
#
#         # Чистим(удаляет) весь лист
#         array_clear = {}
#         clear_table = service.clear(spreadsheetId=SAMPLE_SPREADSHEET_ID,
#                                     range=SAMPLE_RANGE_NAME,
#                                     body=array_clear).execute()
#
#         # добавляет информации
#         array = {'values': dict_cards}
#         response = service.append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
#                                   range=SAMPLE_RANGE_NAME,
#                                   valueInputOption='USER_ENTERED',
#                                   insertDataOption='OVERWRITE',
#                                   body=array).execute()
#
#     except HttpError as err:
#         print(err)


def main():
    start_time = datetime.now()

    get_data()
    # schedule.every(1).second.do(get_data)
    # while True:
    #     schedule.run_pending()

    finish_time = datetime.now()
    spent_time = finish_time - start_time
    print(spent_time)


if __name__ == '__main__':
    main()
