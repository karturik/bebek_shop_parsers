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
    file_name = img_url.replace('https://www.dundarlarbebetoptan.com/resimler/', '')
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
        session.get('https://www.dundarlarbebetoptan.com/site/change_language/tr')
        r = session.get("https://www.dundarlarbebetoptan.com/")

    soup = BeautifulSoup(r.content, features='html.parser')
    main_category_blocks = soup.find_all('div', class_='row subMenu w100 col-sm-m0')
    all_categories = {}
    for main_category_block in main_category_blocks:
        main_category_name = main_category_block.find('div', 'col title').text
        little_categories_blocks = main_category_block.find_all('div', 'col-12 col-lg-6')
        tmp_list = []
        for block in little_categories_blocks:
            tmp_list.append(block.find('a').get('href'))
        all_categories[main_category_name] = tmp_list
    return all_categories


def get_product_links(all_categories):
    all_product_links = {}
    for K1, category_links in all_categories.items():
        product_links_list = []
        for category_link in category_links:
            for i in range(1, 15):
                r = requests.get(category_link + f'?&sayfa={i}')
                soup = BeautifulSoup(r.content, features='html.parser')
                product_links = soup.find_all('a', class_='visual block pos-r')
                if product_links:
                    product_links_list += list(link.get('href') for link in product_links)
                else:
                    break
        all_product_links[K1] = product_links_list

    for key, value in all_product_links.items():
        print(key, len(value))

    return all_product_links


def cart_cleaner(driver):
    driver.get('https://www.dundarlarbebetoptan.com/site/sepetim')
    delete_urls = []
    links = driver.find_elements(By.XPATH, "//a[contains(@href, 'https://www.dundarlarbebetoptan.com/site/sepet_urun_sil')]")
    for link in links:
        delete_urls.append(link.get_attribute('href'))
    for i in delete_urls:
        driver.get(i)

def change_new_category(K2, name, K1):
    K2_new = K2
    if re.search(r"\b" + re.escape('ERKEK') + r"\b", K1.upper()) or re.search(r"\b" + re.escape('ERKEK') + r"\b", K2.upper()):
        if re.search(r"\b" + re.escape('TİŞÖRT'.upper()) + r"\b", name.upper()) or re.search(r"\b" + re.escape('TİŞÖRT'.upper()) + r"\b", K2.upper()) or re.search(r"\b" + re.escape('T-SHİRT'.upper()) + r"\b", name.upper()) or re.search(r"\b" + re.escape('T-SHİRT'.upper()) + r"\b", K2.upper()):
            K2_new = 'FUTBOLKI'
        elif re.search(r"\b" + re.escape('SWEAT'.upper()) + r"\b", name.upper()) or re.search(r"\b" + re.escape('SWEAT'.upper()) + r"\b", K2.upper()) or re.search(r"\b" + re.escape('BADİ'.upper()) + r"\b", name.upper()) or re.search(r"\b" + re.escape('BADİ'.upper()) + r"\b", K2.upper()) or re.search(r"\b" + re.escape('U.KOLLU'.upper()) + r"\b", name.upper()) or re.search(r"\b" + re.escape('U.KOLLU'.upper()) + r"\b", K2.upper()):
            K2_new = 'KOFTY'
        elif re.search(r"\b" + re.escape('ŞORT-KAPRİ') + r"\b", name.upper()) or re.search(r"\b" + re.escape('ŞORT-KAPRİ') + r"\b", K1.upper()):
            K2_new = 'SHORTY'
        elif re.search(r"\b" + re.escape('KOT'.upper()) + r"\b", name.upper()) or re.search(r"\b" + re.escape('KOT'.upper()) + r"\b", K2.upper()) or re.search(r"\b" + re.escape('JOGGER'.upper()) + r"\b", name.upper()) or re.search(r"\b" + re.escape('JOGGER'.upper()) + r"\b", K2.upper()) or re.search(r"\b" + re.escape('PANT'.upper()) + r"\b", name.upper()) or re.search(r"\b" + re.escape('PANT'.upper()) + r"\b", K2.upper()):
            K2_new = 'DZHINSY'

    elif re.search(r"\b" + re.escape('KIZ') + r"\b", K1.upper()) or re.search(r"\b" + re.escape('KIZ') + r"\b", K2.upper()):
        if re.search(r"\b" + re.escape('BADİ') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('BADİ') + r"\b", name.upper()) or re.search(r"\b" + re.escape('TİŞÖRT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('TİŞÖRT') + r"\b", name.upper()):
            K2_new = 'FUTBOLKI'
        elif re.search(r"\b" + re.escape('SWEAT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('SWEAT') + r"\b", name.upper()):
            K2_new = 'KOFTY'
        elif re.search(r"\b" + re.escape('GABARDİN') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('GABARDİN') + r"\b", name.upper()):
            K2_new = 'BRUKI'
        elif re.search(r"\b" + re.escape('PANT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('PANT') + r"\b", name.upper()) or re.search(r"\b" + re.escape('KOT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KOT') + r"\b", name.upper()):
            K2_new = 'DZHINSY'
        elif re.search(r"\b" + re.escape('ŞORT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ŞORT') + r"\b", name.upper()):
            K2_new = 'SHORTY'
        elif re.search(r"\b" + re.escape('TEK ALT - TAYT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('TEK ALT - TAYT') + r"\b", name.upper()):
            K2_new = 'LOSINI'
        elif re.search(r"\b" + re.escape('KAPRİ') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KAPRİ') + r"\b", name.upper()):
            K2_new = 'KAPRI'
        elif re.search(r"\b" + re.escape('ELBİSE-JİLE-TUNİK') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ELBİSE-JİLE-TUNİK') + r"\b", name.upper()):
            K2_new = 'PLATJA'
        elif re.search(r"\b" + re.escape('ETEK') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ETEK') + r"\b", name.upper()) or re.search(r"\b" + re.escape('ELBİSE-JİLE-TUNİK') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ELBİSE-JİLE-TUNİK') + r"\b", name.upper()) or re.search(r"\b" + re.escape('BEBE TULUM') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('BEBE TULUM') + r"\b", name.upper()) or re.search(r"\b" + re.escape('KIYAFET TAKIM') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KIYAFET TAKIM') + r"\b", name.upper()):
            K2_new = 'JUBKI'

    elif 'BEBE' in K1.upper() or 'BEBE' in K2.upper():
        if re.search(r"\b" + re.escape('KİLOTLU ÇORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KİLOTLU ÇORAP') + r"\b", name.upper()) or re.search(r"\b" + re.escape('KÜLOTLU ÇORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KÜLOTLU ÇORAP') + r"\b", name.upper()):
            K2_new = 'KOLGOTKI'
        elif re.search(r"\b" + re.escape('ÇORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ÇORAP') + r"\b", name.upper()):
            K2_new = 'NOSKI'
        elif re.search(r"\b" + re.escape('ÇAMAŞIR - ALIŞTIRMA KÜLOTU') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ÇAMAŞIR - ALIŞTIRMA KÜLOTU') + r"\b", name.upper()):
            K2_new = 'BELJE'
        elif re.search(r"\b" + re.escape('PATİK') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('PATİK') + r"\b", name.upper()):
            K2_new = 'PINETKI'
    return K2_new


def get_product_data(product_links_dict, driver, w_file):
    for K1_main, product_links in tqdm(product_links_dict.items()):
        for product_link in tqdm(product_links):
            try:
                if product_links.index(product_link) % 50 == 0:
                    cart_cleaner(driver)
                driver.get(product_link)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="eAdet"]')))
                product_url = driver.current_url
                img_buttons = driver.find_elements(By.CLASS_NAME, 'img-fluid.cur-p.col-sm-ha')
                imgs_list_tmp = set()
                try:
                    for img_button in img_buttons:
                        img_button.click()
                        img = driver.find_element(By.XPATH, '//*[@id="detay"]/div/div/div/div/div[2]/div/div/img[1]')
                        src = img.get_attribute("src")
                        imgs_list_tmp.add(src)
                except Exception as e:
                    # print(e)
                    pass
                soup = BeautifulSoup(driver.page_source, features="html.parser")
                try:
                    count_field = driver.find_element(By.XPATH, '//*[@id="eAdet"]')
                    count_field.send_keys('1000')
                    count_field.send_keys(Keys.ENTER)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "sweet-alert.showSweetAlert.visible")))
                    count_text = driver.find_element(By.CLASS_NAME, 'sweet-alert.showSweetAlert.visible').text
                    if count_text:
                        if 'Stok nedeniyle ekleme yapılamıyor' in count_text:
                            checker = 0
                        else:
                            try:
                                checker = count_text.split('yerine ')[1].split(' adet')[0]
                            except Exception as e:
                                print(e)
                                checker = 0
                        print(checker)
                except Exception as e:
                    print(e)
                    checker = 0
                if int(checker) >= request_count:
                    name = soup.find("div", class_="col-12 urunIsmi col-sm-mt3 lh26").text
                    name = name.replace("  ", " ").replace("\n", " ").strip()
                    K2 = soup.find("div", class_="col-12 breadCrumb-desktop").find_all('a')[-1].text.strip()
                    K2 = change_new_category(K2, name, K1_main)
                    K1 = "DDL " + K1_main + ' - ' + K2
                    price = soup.find("span", class_="col-12 price-TL col-sm-fs17").text.replace('TL', '').strip()
                    price = price.replace("  ", "").replace("\n", "").replace("₺", "").replace("$", "").replace("-", "").strip()
                    # aciklama = soup.find("span", class_="w100 left fw6 col-xs-fw3 col-xs-op8 colored5 fs16 lh20 mt5 ceviri_def").text.replace(" ", "").replace("\n", "") + " وصف"
                    urun_kodu = driver.find_element(By.XPATH, "/html/head/meta[6]").get_attribute('content').split(',')[0]
                    urun_kodu = "DDL" + urun_kodu.replace("  ", "").replace("\n", "")
                    try:
                        paket_adedi = ''
                        paket_adedi_cols = soup.find_all("div", class_="col-3 col-lg-3")
                        for paket_adedi_col in paket_adedi_cols:
                            if 'Paket' in paket_adedi_col.text:
                                paket_adedi = paket_adedi_col.find('span', class_='urunBilgi-icerik').text
                        paket_adedi = paket_adedi.replace(" ", "").replace("\n", "").replace("Adet", "").strip()
                    except:
                        paket_adedi = ''
                    brand = soup.find("a", class_="fw7 fs14 block colored col-sm-pl0 col-sm-mb2").text.strip()
                    size = list(word for word in driver.find_element(By.XPATH, "/html/head/meta[6]").get_attribute('content').split(' ') if '-' in word and re.search(r'\d', word))
                    if size:
                        size = size[0].replace("  ", "").replace("\n", "").replace(",", "").strip()
                        for i in size.split('-'):
                            if len(i) > 2:
                                try:
                                    int(i)
                                    size = ''
                                except:
                                    pass
                    else:
                        size = ''
                    if size:
                        if not 'ay' in size.lower() and not 'y' in size.lower() and 'ay' in driver.find_element(By.XPATH, "/html/head/meta[6]").get_attribute('content').lower():
                            size = size + 'AY'
                        if not 'YAŞ' in size.upper() and not 'y' in size.lower() and 'YAŞ' in driver.find_element(By.XPATH, "/html/head/meta[6]").get_attribute('content').upper():
                            size = size + 'YAŞ'
                        if not 'NO' in size.upper() and not 'y' in size.lower() and 'NO' in driver.find_element(By.XPATH, "/html/head/meta[6]").get_attribute('content').upper():
                            size = size + 'NO'
                        if not 'Y' in size.upper() and not 'NO' in size.upper():
                            size = size + 'Y'
                        if size == '8-12':
                            size = size + 'YAŞ'
                        size = size.upper().replace('NO', ' NO').replace('YAŞ', ' YAŞ').replace('AY', ' AY').replace('TK.', '').replace('--', '-').replace('1824', '18-24') \
                            .replace('ELBİSE', '').replace('99', '9').replace('06', '6').replace('NO AY', 'NO').replace('KÜÇÜK', '').replace('-Y', ' Y') \
                            .replace('4Y', '4 Y').replace('2Y', '2 Y').replace('8Y', '8 Y').replace('11Y', '11 Y').replace('16Y', '16 Y').replace('15Y', '15 Y') \
                            .replace('17Y', '17 Y').replace('6Y', '6 Y').replace('5Y', '5 Y').replace('7Y', '7 Y').replace('10Y', '10 Y') \
                            .replace('12Y', '12 Y').replace('15Y', '15 Y').replace('NOY', 'NO') \
                            .replace('42Y', '42 NO').replace('42 AY', '42 NO')
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
                    try:
                        sezon = ''
                        sezon_cols = soup.find_all("div", class_="col-3 col-lg-3")
                        for sezon_col in sezon_cols:
                            if 'Mevs' in sezon_col.text:
                                sezon = sezon_col.find('span', class_='urunBilgi-icerik').text
                        sezon = sezon.replace(" ", "").replace("\n", "").replace("Adet", "").strip()
                    except:
                        sezon = ''
                    row = f"{product_url}#{K1}#{K2}#{name}#{price}#{''}#{''}#{''}#{''}#{brand}" \
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
    # prefs = {'profile.default_content_setting_values': {'images': 2, 'plugins': 2, 'geolocation': 2,
    #                                                     'notifications': 2, 'auto_select_certificate': 2,
    #                                                     'fullscreen': 2,
    #                                                     'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
    #                                                     'media_stream_mic': 2, 'media_stream_camera': 2,
    #                                                     'protocol_handlers': 2,
    #                                                     'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
    #                                                     'push_messaging': 2, 'ssl_cert_decisions': 2,
    #                                                     'metro_switch_to_desktop': 2,
    #                                                     'protected_media_identifier': 2, 'app_banner': 2,
    #                                                     'durable_storage': 2}}
    # options.add_experimental_option('prefs', prefs)
    # options.add_argument("--disable-infobars")
    # options.add_argument("--disable-extensions")
    # options.add_argument('--blink-settings=imagesEnabled=false')
    # # options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get('https://www.dundarlarbebetoptan.com/uye/giris')
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
    password.send_keys(Keys.ENTER)

    cart_cleaner(driver)

    driver.get("https://www.dundarlarbebetoptan.com/site/change_language/tr")

    category_links = get_categories_links()

    product_links = get_product_links(category_links)

    all_links = []
    for value in product_links.values():
        all_links += value

    print('Всего товаров найдено: ', len(all_links))

    with open(f"dundarlarbebetoptan {date}.csv", "w", encoding='utf-8') as w_file:
        w_file.write("url#K1#K2#Name#Price 1#Price 2#Açıklama#BEDEN SEÇİNİZ#BİRİM ( 1 Adet ) FİYATI#"
                     "Brand#Code#Count#Paket Adedi#PAKET FİYATI ( 4 Adet )#"
                     "PAKET SAYISI SEÇİNİZ#Ürün Açıklaması#Ürün Detayları#Ürün Kodu#"
                     "Yaş Grubu#Size#IMGs#Renkle#IMG 1#IMG 2#IMG 3#IMG 4#IMG 5#"
                     "IMG 6#IMG 7#IMG 8#IMG 9#IMG 10#IMG 11#IMG 12#"
                     "IMG 13#IMG 14#IMG 15#Renk 1#Renk 2#Renk 3#"
                     "Renk 4#Renk 5#Renk 6#Renk 7#Renk 8#Renk 9#Renk 10#"
                     "Renk 11#Renk 12#Renk 13#Renk 14#Renk 15#sezon#checker" + '\n')

    with open(f"dundarlarbebetoptan {date}.csv", "a", encoding='utf-8') as w_file:
        get_product_data(product_links, driver, w_file)

    read_file = pd.read_csv(f"dundarlarbebetoptan {date}.csv", sep='#')
    read_file.to_excel(f"dundarlarbebetoptan {date}.xlsx", index=False)

main()