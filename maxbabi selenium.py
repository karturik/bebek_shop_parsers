import time
import requests
import csv
import datetime
import re

from bs4 import BeautifulSoup

import pandas as pd
from openpyxl import Workbook

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import boto3
import botocore
from tqdm import tqdm

e = datetime.datetime.now()
startTime = e
date = f"{'%s.%s.%s %s-%s-%s' % (e.day, e.month, e.year, e.hour, e.minute, e.second)}"

request_count = 20

categories = {"BEBE GİYİM": ['BEBEK TAKIM', 'BEBEK ELBİSE-JİLE-ETEK', 'SALOPET', 'BEBEK ZIBIN-HASTANE ÇIKIŞI SETİ', 'BEBEK ÇITÇITLI BODY',
                             'ATLET-KÜLOT', 'KAZAK', 'BEBEK YELEK-HIRKA', 'BEBEK TEK ALT', 'SWEAT', 'PANTOLON', 'BEBEK MEVLİT TAKIM',
                             'BEBEK KOZMONOT-MONT', 'KIZ BEBEK TAKIM', 'ERKEK BEBEK TAKIM', 'PİJAMA TAKIMI', 'BEBEK TULUM'],
              "ÇOCUK GİYİM": ['KIZ ÇOCUK TAKIM', 'ERKEK ÇOCUK TAKIM', 'ÇOCUK CEKET-MONT-HIRKA', 'ÇOCUK TULUM', 'ÇOCUK ELBİSE-JİLE-ETEK',
                              'PANTOLON', 'GÖMLEK', 'ÇOCUK PİJAMA TAKIMI', 'KIZ ÇOCUK PİJAMA TAKIMI', 'AYAKKABI-BABET'],
              "TRİKO": ['BEBEK TAKIM', 'TULUM', 'TRİKO BODY', 'TRİKO HIRKA-YELEK-MONT', 'TRİKO SET', 'BEBEK BATTANİYE', 'TRİKO BERE BATTANİYE SET',
                        'TRİKO BERE', 'TRİKO ANAKUCAĞI', 'BEBEK AYAKKABI-PATİK'],
              "BEBE ÇEYİZ": ['BEBEK BATTANİYE', 'BEBEK HAVLU', 'BEBEK BORNOZ TAKIMI', 'BEBEK ALT AÇMA', 'NEVRESİM TAKIMI'],
              "AKSESUAR": ['BEBEK PATİK-İLK ADIM AYAKKABISI', 'ÖNLÜK-MENDİL-ELDİVEN-EMZİK ASKISI', 'ŞAPKA-SAÇ BANDI-PAPYON',
                           'BEBEK ÇANTASI', 'ÇORAP']
              }

s3_client = boto3.client(
    service_name = 's3',
    endpoint_url = 'https://s3.eu-central-1.amazonaws.com/',
    aws_access_key_id = 'aws_access_key_id',
    aws_secret_access_key = 'aws_secret_access_key'
)

session = boto3.Session(aws_access_key_id='aws_access_key_id', aws_secret_access_key='aws_secret_access_key')
s3 = session.resource('s3')

object_keys = []

my_bucket = s3.Bucket('Bucket')
for objects in tqdm(my_bucket.objects.filter(Prefix="parsing_data/")):
    object_keys.append(objects.key)

def upload_image_to_s3(img_url) -> str:
    global object_keys
    file_name = img_url.replace('https://www.maxbabi.com/resimler/', '')
    key = f'parsing_data/{file_name}'
    if key in object_keys:
        print('Фото уже есть')
        pass
    else:
        r = requests.get(img_url, stream=True)
        print('Такого фото еще нет, загружаем')
        s3_client.put_object(
            Body=r.content,
            Bucket='Bucket',
            Key=f'parsing_data/{file_name}'
        )
    url = f'https://s3.eu-central-1.amazonaws.com/Bucket/parsing_data/{file_name}'
    return url


def get_categories_links():
    with requests.Session() as session:
        session.get('http://www.maxbabi.com/site/change_language/tr')
        r = session.get("https://www.maxbabi.com/")

    soup = BeautifulSoup(r.content, features='html.parser')
    main_category_blocks = soup.find_all('div', class_='col-4')
    all_categories = []
    all_categories += list(main_category_block.find('a').get('href') for main_category_block in main_category_blocks if 'kategori' in main_category_block.find('a').get('href'))
    return all_categories


def get_product_links(all_categories):
    product_links_list = []
    for category_link in all_categories:
        for i in range(1, 15):
            r = requests.get(category_link + f'?&sayfa={i}')
            soup = BeautifulSoup(r.content, features='html.parser')
            product_links = soup.find_all('a', class_='visual block pos-r')
            if product_links:
                product_links_list += list(link.get('href') for link in product_links)
            else:
                break
    return product_links_list


def cart_cleaner(driver):
    print('Чистим корзину...')
    driver.get('https://www.maxbabi.com/site/sepetim')
    delete_urls = []
    links = driver.find_elements(By.XPATH, "//a[contains(@href, 'https://www.maxbabi.com/site/sepet_urun_sil/')]")
    for link in links:
        delete_urls.append(link.get_attribute('href'))
    for i in delete_urls:
        driver.get(i)


def change_new_category(K2, name, K1):
    K2 = K2
    if re.search(r"\b" + re.escape('KÜLOTLU') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KÜLOTLU') + r"\b", name.upper()):
        K2 = 'KOLGOTKI'
    elif re.search(r"\b" + re.escape('ÇORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ÇORAP') + r"\b", name.upper()):
        K2 = 'NOSKI'
    elif re.search(r"\b" + re.escape('ŞORT-KAPRİ') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ŞORT-KAPRİ') + r"\b", name.upper()):
        K2 = 'SHORTY'
    elif re.search(r"\b" + re.escape('ELBİSE') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ELBİSE') + r"\b", name.upper()) and not re.search(r"\b" + re.escape('CONVERS') + r"\b", name.upper()):
        K2 = 'PLATJA'
    elif re.search(r"\b" + re.escape('ETEK') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ETEK') + r"\b", name.upper()):
        K2 = 'JUBKI'
    elif re.search(r"\b" + re.escape('AYAKKABI-PATİK') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('AYAKKABI-PATİK') + r"\b", name.upper()):
        K2 = 'PINETKI'
    return K2


def get_product_data(product_links_list, driver, w_file):
    for product_link in tqdm(product_links_list):
        try:
            if product_links_list.index(product_link) % 50 == 0:
                cart_cleaner(driver)
            driver.get(product_link)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="eAdet"]')))
            product_url = driver.current_url
            img_buttons = driver.find_elements(By.CLASS_NAME, 'img-fluid.cur-p.col-sm-ha') + driver.find_elements(By.CLASS_NAME, 'img-fluid.cur-p.col-sm-ha.selected')
            imgs_list_tmp = set()
            # print(len(img_buttons))
            if len(img_buttons) < 2:
                try:
                    img_button = driver.find_element(By.XPATH, '//*[@id="detay"]/div/div/div/div/div[3]/div/div[4]/ul/li/img')
                    img_button.click()
                    img = driver.find_element(By.XPATH, '//*[@id="detay"]/div/div/div/div/div[2]/div/div/img[1]')
                    src = img.get_attribute("src")
                    if src and 'https://www.maxbabi.com/resimler/' in src:
                        imgs_list_tmp.add(src)
                except:
                    pass
            else:
                for img_button in img_buttons:
                    img = driver.find_element(By.XPATH, '//*[@id="detay"]/div/div/div/div/div[2]/div/div/img[1]')
                    src = img.get_attribute("src")
                    if src and 'https://www.maxbabi.com/resimler/' in src:
                        imgs_list_tmp.add(src)
                    img_button.click()
                    img = driver.find_element(By.XPATH, '//*[@id="detay"]/div/div/div/div/div[2]/div/div/img[1]')
                    src = img.get_attribute("src")
                    if src and 'https://www.maxbabi.com/resimler/' in src:
                        imgs_list_tmp.add(src)
            soup = BeautifulSoup(driver.page_source, features="html.parser")
            count_field = driver.find_element(By.XPATH, '//*[@id="eAdet"]')
            count_field.send_keys('1000')
            count_field.send_keys(Keys.ENTER)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sweet-alert.showSweetAlert.visible")))
            count_text = driver.find_element(By.CLASS_NAME, 'sweet-alert.showSweetAlert.visible').text
            try:
                if 'Stok nedeniyle ekleme yapılamıyor' in count_text:
                    checker = 0
                else:
                    checker = count_text.split('yerine ')[1].split(' adet')[0]
            except IndexError:
                checker = 0
            print(checker)
            if int(checker) >= request_count:
                name = soup.find("div", class_="col-12 urunIsmi").text
                name = name.replace("  ", " ").replace("\n", " ").strip()
                K2 = soup.find("div", class_="col-12 breadCrumb-desktop").find_all('a')[-1].text.strip()
                K1 = ''
                for key, value in categories.items():
                    if K2 in value:
                        K1 = key
                K2 = change_new_category(K2, name, K1)
                K1 = "XBA " + K1 + " - " + K2
                brand = soup.find('a', class_='fw7 fs14 block colored2 col-sm-pl0').text.strip()
                price = soup.find("span", class_="data mainPrice").text
                price = price.replace("  ", "").replace("\n", "").replace("₺", "").replace("$", "").replace("-", "").strip()
                if soup.find_all("div", class_="col-12 aciklamaText"):
                    aciklama = soup.find("div", class_="col-12 aciklamaText").text.replace(" ", "").replace("\n", "").replace("&nbsp;", " ").replace(" ", " ")
                else:
                    aciklama = ''
                urun_kodu = soup.find('div', class_='col-12 categoryName urunKodu').text.replace(soup.find('a', class_='fw7 fs14 block colored2 col-sm-pl0').text, '')
                urun_kodu = "XBA-" + urun_kodu.replace("  ", "").replace("\n", "").replace("#", "")
                descr = soup.find_all('div', class_='col-3 col-lg-3')
                size = ''
                sezon = ''
                paket_adedi = ''
                for col in descr:
                    desc_name = col.find('span', class_='urunBilgi-baslik').text
                    desc_text = col.find('span', class_='urunBilgi-icerik').text.replace("  ", "").replace("\n", "").replace(",", "").replace("Adet", "").strip()
                    if 'Yaş' in desc_name:
                        size = desc_text
                    elif 'Mevsim' in desc_name:
                        sezon = desc_text
                    elif 'Paket Adedi' in desc_name:
                        paket_adedi = desc_text

                imgs_list = list((upload_image_to_s3(src)) for src in imgs_list_tmp)
                imgs = ";".join(imgs_list)
                imgs_row = list([] for i in range(1, 16))
                for x in range(0, 15):
                    try:
                        imgs_row[x] = list(imgs_list)[x]
                    except Exception as e:
                        imgs_row[x] = " "
                renkle = ';'.join(list(renk.text.replace("  ", "").replace("\n", "").replace("-+", "; ").lower() for renk in soup.find_all("span", class_="renkName")))
                renkle_list = renkle.split(";")
                renkle_row = list([] for i in range(1, 16))
                for x in range(0, 15):
                    try:
                        renkle_row[x] = renkle_list[x].upper()
                    except Exception as e:
                        renkle_row[x] = " "

                row = f"{product_url}#{K1}#{K2}#{name}#{price}#{''}#{aciklama}#{''}#{''}#{brand}" \
                      f"#{''}#{''}#{paket_adedi}#{''}#{''}#{''}#{''}#{urun_kodu}" \
                      f"#{''}#{size}#{imgs}#{renkle}#{'#'.join(imgs_row)}#{'#'.join(renkle_row)}#{sezon}#{checker}"

                write_row = row.split("#")
                print(write_row)

                if write_row[0] != '' and write_row[1] != '' and write_row[2] != '' and write_row[3] != '':
                    if len(write_row) > 40:
                        w_file.write(row + '\n')
                    else:
                        print(write_row)
                else:
                    pass
            else:
                print('Мало товара')
        except:
            pass


def main():
    options = Options()
    prefs = {'profile.default_content_setting_values': {'images': 2, 'plugins': 2, 'geolocation': 2,
                                                        'notifications': 2, 'auto_select_certificate': 2,
                                                        'fullscreen': 2,
                                                        'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
                                                        'media_stream_mic': 2, 'media_stream_camera': 2,
                                                        'protocol_handlers': 2,
                                                        'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
                                                        'push_messaging': 2, 'ssl_cert_decisions': 2,
                                                        'metro_switch_to_desktop': 2,
                                                        'protected_media_identifier': 2, 'app_banner': 2,
                                                        'durable_storage': 2}}
    # options.add_experimental_option('prefs', prefs)
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument('--blink-settings=imagesEnabled=false')
    # options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1024,720")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get("http://www.maxbabi.com/site/change_language/tr")
    driver.get('https://www.maxbabi.com/uye/giris')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "e_email")))
    login = driver.find_element(By.ID, 'e_email')
    login.clear()
    login.send_keys('login')
    time.sleep(2)
    password = driver.find_element(By.ID, 'e_sifre')
    password.clear()
    password.send_keys('password')
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="girisForm"]/div[3]/div[2]/button').click()
    time.sleep(1)

    cart_cleaner(driver)

    category_links = get_categories_links()

    product_links = get_product_links(category_links)

    print('Всего товаров найдено: ', len(product_links))

    with open(f"maxbabi {date}.csv", "w", encoding='utf-8') as w_file:
        w_file.write("url#K1#K2#Name#Price 1#Price 2#Açıklama#BEDEN SEÇİNİZ#BİRİM ( 1 Adet ) FİYATI#"
                     "Brand#Code#Count#Paket Adedi#PAKET FİYATI ( 4 Adet )#"
                     "PAKET SAYISI SEÇİNİZ#Ürün Açıklaması#Ürün Detayları#Ürün Kodu#"
                     "Yaş Grubu#Size#IMGs#Renkle#IMG 1#IMG 2#IMG 3#IMG 4#IMG 5#"
                     "IMG 6#IMG 7#IMG 8#IMG 9#IMG 10#IMG 11#IMG 12#"
                     "IMG 13#IMG 14#IMG 15#Renk 1#Renk 2#Renk 3#"
                     "Renk 4#Renk 5#Renk 6#Renk 7#Renk 8#Renk 9#Renk 10#"
                     "Renk 11#Renk 12#Renk 13#Renk 14#Renk 15#sezon#checker" + '\n')

    with open(f"maxbabi {date}.csv", "a", encoding='utf-8') as w_file:
        get_product_data(product_links, driver, w_file)

    read_file = pd.read_csv(f"maxbabi {date}.csv", sep='#')
    read_file.to_excel(f"maxbabi {date}.xlsx", index=False)

main()