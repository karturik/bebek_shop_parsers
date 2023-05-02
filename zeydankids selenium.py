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
from selenium.common.exceptions import TimeoutException

import boto3
import botocore
from tqdm import tqdm

e = datetime.datetime.now()
startTime = e
date = f"{'%s.%s.%s %s-%s-%s' % (e.day, e.month, e.year, e.hour, e.minute, e.second)}"


categories = {'ERKEK ÇOCUK GİYİM': ['Erkek Çocuk Tişört', 'Erkek Çocuk Takım', 'Erkek Çocuk Pantolon', 'Erkek Çocuk Kapri - Şort', 'Erkek Çocuk Gömlek',
                                    'Erkek Çocuk Eşofman Tek Alt', 'Erkek Çocuk Mont - Yelek - Ceket',
                                    'Erkek Çocuk Pijama', 'Erkek Çocuk İç Çamaşır - Çorap',
                                    'Erkek Çocuk Kazak - Hırka - Triko'],
              'KIZ ÇOCUK GİYİM': ['Kız Çocuk Takım', 'Kız Çocuk Pantolon', 'Kız Çocuk Tişört - Badi',
                                  'Kız Çocuk Elbise - Jile', 'Kız Çocuk İç Çamaşır - Çorap', 'Kız Çocuk Gömlek - Tunik', 'Kız Çocuk Eşofman Tek Alt',
                                  'Kız Çocuk Pijama', 'Kız Çocuk Mont - Yelek - Ceket - Bolero', 'Kız Çocuk Etek - Kapri - Şort', 'Kız Çocuk Tayt',
                                  'Kız Çocuk Kazak - Hırka - Triko'],
              'BEBEK GİYİM': ['Bebek Erkek Takım', 'Bebek Tulum',
                              'Bebek Kız Takım', 'Zıbın Seti 2-3-5-7 Parça', 'Bebek Elbise - Jile', 'Bebek Badi',
                              'Zıbın Seti 10-11-12 Parça', 'Bebek Badili Takım', 'Bebek Tek Alt - Tek Üst',
                              'Bebek Pijama', 'Bebek Yelek - Hırka'],
              'BEBEK ÇEYİZ': ['Bornoz - Havlu', 'Önlük - Mendil', 'Battaniye', 'Çorap', 'Patik - Ayakkabı',
                              'Şapka - Bandana', 'Çanta - Bebek Taşıma Seti', 'Alt Açma - Kundak',
                              'Aksesuar', 'Mevlütlük Takım', 'İç Çamaşır - Alıştırma Külot']
              }

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
    file_name = img_url.replace('https://zeydankids.sercdn.com/resimler/', '')
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
    r = requests.get("https://www.zeydankids.com/")
    soup = BeautifulSoup(r.content, features='html.parser')
    category_links = soup.find_all('a', class_='lh30 block ellipsis col-sm-fn colored')
    category_links = set(link.get('href') for link in category_links)
    print(category_links)
    return category_links


def get_product_links(category_links, driver):
    all_product_links = []
    for category_link in category_links:
        for i in range(1, 15):
            r = requests.get(category_link + f'?&sayfa={i}')
            soup = BeautifulSoup(r.content, features='html.parser')
            product_links = soup.find_all('div', class_='owl-carousel owl-theme owlControl b-white b-ra20')
            if len(product_links) != 0:
                print(category_link + f'?&sayfa={i}')
                all_product_links += list(link.find('a').get('href') for link in product_links if link.find('a'))
            else:
                break

    all_product_links = list(set(all_product_links))
    print('Всего товаров найдено: ', len(all_product_links))
    return all_product_links


def cart_cleaner(driver):
    print('Чистим корзину')
    driver.get('https://www.zeydankids.com/site/sepetim')
    delete_urls = []
    links = driver.find_elements(By.XPATH, "//a[contains(@href, 'https://www.zeydankids.com/site/sepet_urun_sil/')]")
    for link in links:
        delete_urls.append(link.get_attribute('href'))
    for link in tqdm(delete_urls):
        success = False
        while success != True:
            try:
                driver.get(link)
                # driver.set_page_load_timeout(5)
                success = True
            except TimeoutException:
                driver.refresh()

def change_new_category(K2, name, K1):
    new_K2 = K2
    if 'ERKEK' in K2.upper() or 'ERKEK' in K1.upper():
        if re.search(r"\b" + re.escape('Çocuk Tişört') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('Çocuk Tişört') + r"\b", name.upper()):
            new_K2 = 'FUTBOLKI'
        elif re.search(r"\b" + re.escape('KÜLOTLU') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KÜLOTLU') + r"\b", name.upper()):
            new_K2 = 'KOLGOTKI'
        elif re.search(r"\b" + re.escape('CORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('CORAP') + r"\b", name.upper()) or re.search(r"\b" + re.escape('ÇORABI') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ÇORABI') + r"\b", name.upper()):
            new_K2 = 'NOSKI'
        elif re.search(r"\b" + re.escape('ATLET') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ATLET') + r"\b", name.upper()) or re.search(r"\b" + re.escape('KULOT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KULOT') + r"\b", name.upper()) or re.search(r"\b" + re.escape('BOXER') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('BOXER') + r"\b", name.upper()) or re.search(r"\b" + re.escape('CAMASIR') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('CAMASIR') + r"\b", name.upper()):
            new_K2 = 'BELJE'
        elif re.search(r"\b" + re.escape('Kapri - Şort') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('Kapri - Şort') + r"\b", name.upper()):
            new_K2 = 'SHORTY'
        elif re.search(r"\b" + re.escape('KOT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KOT') + r"\b", name.upper()):
            new_K2 = 'DZHINSY'
    elif 'KIZ' in K2.upper() or 'KIZ' in K1.upper():
        if re.search(r"\b" + re.escape('Tişört - Badi') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('Tişört - Badi') + r"\b", name.upper()):
            new_K2 = 'FUTBOLKI'
        elif re.search(r"\b" + re.escape('KİLOTLU CORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KİLOTLU CORAP') + r"\b", name.upper()) or re.search(r"\b" + re.escape('KİLOTLU') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KİLOTLU') + r"\b", name.upper()) or re.search(r"\b" + re.escape('KÜLOTLU ÇORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KÜLOTLU ÇORAP') + r"\b", name.upper()):
            new_K2 = 'KOLGOTKI'
        elif re.search(r"\b" + re.escape('ÇORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ÇORAP') + r"\b", name.upper()) or re.search(r"\b" + re.escape('CORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('CORAP') + r"\b", name.upper()) or re.search(r"\b" + re.escape('BABET') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('BABET') + r"\b", name.upper()):
            new_K2 = 'NOSKI'
        elif re.search(r"\b" + re.escape('KULOT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KULOT') + r"\b", name.upper()) or re.search(r"\b" + re.escape('SLIP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('SLIP') + r"\b", name.upper()) or re.search(r"\b" + re.escape('BÜSTİYER') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('BÜSTİYER') + r"\b", name.upper()) or re.search(r"\b" + re.escape('BOXER') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('BOXER') + r"\b", name.upper()) or re.search(r"\b" + re.escape('ATLET') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ATLET') + r"\b", name.upper()) or re.search(r"\b" + re.escape('takım') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('takım') + r"\b", name.upper()):
            new_K2 = 'BELJE'
        elif re.search(r"\b" + re.escape('şort') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('şort') + r"\b", name.upper()):
            new_K2 = 'SHORTY'
        elif re.search(r"\b" + re.escape('KOT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KOT') + r"\b", name.upper()):
            new_K2 = 'DZHINSY'
        elif re.search(r"\b" + re.escape('Kız Çocuk Tayt') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('Kız Çocuk Tayt') + r"\b", name.upper()):
            new_K2 = 'LOSINI'
        elif re.search(r"\b" + re.escape('KAPRİ') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KAPRİ') + r"\b", name.upper()):
            new_K2 = 'KAPRI'
        elif re.search(r"\b" + re.escape('Elbise - Jile') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('Elbise - Jile') + r"\b", name.upper()):
            new_K2 = 'PLATJA'
        elif re.search(r"\b" + re.escape('ETEK') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ETEK') + r"\b", name.upper()) and not re.search(r"\b" + re.escape('Elbise - Jile') + r"\b", K2.upper()) and not re.search(r"\b" + re.escape('Elbise - Jile') + r"\b", name.upper()) and 'Kapri - Şort' in K2.upper():
            new_K2 = 'JUBKI'
    elif 'BEBEK' in K2.upper() or 'BEBEK' in K1.upper():
        if re.search(r"\b" + re.escape('KULOTLU CORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KULOTLU CORAP') + r"\b", name.upper()) or re.search(r"\b" + re.escape('KÜLOTLU ÇORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KÜLOTLU ÇORAP') + r"\b", name.upper()) or re.search(r"\b" + re.escape('KİLOTLU') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('KİLOTLU') + r"\b", name.upper()):
            new_K2 = 'KOLGOTKI'
        elif re.search(r"\b" + re.escape('CORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('CORAP') + r"\b", name.upper()):
            new_K2 = 'NOSKI'
        elif 'İç Çamaşır - Alıştırma Külot'.upper() in K2.upper() or 'İç Çamaşır - Alıştırma Külot'.upper() in name.upper():
            new_K2 = 'BELJE'
        elif 'Patik - Ayakkabı'.upper() in K2.upper() or 'Patik - Ayakkabı'.upper() in name.upper():
            new_K2 = 'PINETKI'
    return new_K2

def get_product_data(product_links, driver, w_file):
    for product_link in tqdm(product_links):
        success = False
        while success != True:
            try:
                if product_links.index(product_link) % 50 == 0:
                    cart_cleaner(driver)
                driver.get(product_link)
                # driver.set_page_load_timeout(5)
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'/html/body/main/content/section[1]/div[2]/div[3]/div/div[2]/div/div[6]/form/div/div[3]/div/div/input')))
                soup = BeautifulSoup(driver.page_source, features="html.parser")
                product_url = driver.current_url
                count_field = driver.find_element(By.XPATH,
                                                  '/html/body/main/content/section[1]/div[2]/div[3]/div/div[2]/div/div[6]/form/div/div[3]/div/div/input')
                success = False
                while not success:
                    count_field.click()
                    count_field.send_keys('1000')
                    count_field.send_keys(Keys.ENTER)
                    success = True
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sweet-alert.showSweetAlert.visible")))
                count_text = driver.find_element(By.CLASS_NAME, 'sweet-alert.showSweetAlert.visible').text
                if 'Stok nedeniyle ekleme yapılamıyor' in count_text:
                    checker = 0
                else:
                    try:
                        checker = count_text.split('yerine ')[1].split(' adet')[0]
                    except:
                        checker = 0
                print(checker)
                if int(checker) >= request_count:
                    K2 = ''
                    for meta in soup.find_all('meta'):
                        if 'ziyaret edin' in meta.get('content'):
                            K2 = meta.get('content').split('toptan')[1].replace('çeşitleri için sitemizi ziyaret edin.', '').strip()
                    K1 = ''
                    for key, value in categories.items():
                        if K2 in value:
                            K1 = key
                    name = soup.find("a", class_="colored2 fw7").text.strip().replace('-', ' - ').replace('(MEVSİMLİK)', ' (MEVSİMLİK)')
                    K2 = change_new_category(K2, name, K1)
                    K1 = "ZNK " + K1 + " - " + K2
                    price = soup.find("div", class_="fs30 lh30 op8 flex col-sm-fs26 col-sm-lh26").text.strip()
                    paket_adedi = soup.find_all("div", class_="colored op8 fw7 fs16 lh16 col-sm-fs14 col-sm-lh14")[2].text.strip()
                    urun_kodu = "ZNK-" + soup.find("div", class_="col-12 colored3 fw7 fs16 lh16").text.replace("#", "")
                    brand = soup.find_all("div", class_="colored op8 fw7 fs16 lh16 col-sm-fs14 col-sm-lh14")[3].text.strip()
                    size = soup.find_all("div", class_="colored op8 fw7 fs16 lh16 col-sm-fs14 col-sm-lh14")[0].text.strip()
                    imgs_list = []
                    for img in set(img.get("src") for img in soup.find_all("img", class_="img-fluid b-ra5 soft cur-p p7 mb15 col-sm-mb5") + soup.find_all("img", class_="img-fluid b-ra5 soft cur-p p7 mb15 col-sm-mb5 selected")):
                        imgs_list.append(upload_image_to_s3(img))
                    imgs = "; ".join(imgs_list)
                    imgs_row = list([] for i in range(1, 16))
                    for x in range(0, 15):
                        try:
                            imgs_row[x] = imgs_list[x]
                        except Exception as e:
                            imgs_row[x] = " "
                    renkle_list = []
                    renkle = soup.find_all("span", class_="block t-center fs12 colored lh12 mt2 op8 fw5 col-sm-mb5")
                    for renk in renkle:
                        renk = renk.text.strip().lower()
                        renkle_list.append(renk)
                    renkle = "; ".join(renkle_list)
                    renkle_row = list([] for i in range(1, 16))
                    for x in range(0, 15):
                        try:
                            renkle_row[x] = renkle_list[x].upper()
                        except Exception as e:
                            renkle_row[x] = " "
                    if ' ay' in renkle or ' yaş' in renkle or ' yas' in renkle:
                        # yas_grubu = renkle
                        size = renkle
                        renkle = ''
                        renkle_row = []
                    sezon = soup.find_all("div", class_="colored op8 fw7 fs16 lh16 col-sm-fs14 col-sm-lh14")[1].text.strip()

                    row = f"{product_url}|{K1}|{K2}|{name}|{price}|{''}|{''}|{''}|{''}|{brand}" \
                          f"|{''}|{''}|{paket_adedi}|{''}|{''}|{''}|{''}|{urun_kodu}" \
                          f"|{''}|{size}|{imgs}|{renkle}|{'|'.join(imgs_row)}|{'|'.join(renkle_row)}|{sezon}|{checker}"

                    write_row = row.split('|')
                    print(write_row)

                    if write_row[0] != '' and write_row[1] != '' and write_row[2] != '' and write_row[3] != '':
                        if len(write_row) > 40:
                            w_file.write(row + '\n')
                        else:
                            pass
                else:
                    print('Мало товара')
                success = True
            except TimeoutException as e:
                driver.refresh()
            except Exception as e:
                print(e)
                pass


def main():
    options = Options()
    options.add_argument("--headless")
    prefs = {'profile.default_content_setting_values': {'images': 2}}
    options.add_experimental_option('prefs', prefs)
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1024,720")
    driver = webdriver.Chrome(options=options)

    driver.get('https://www.zeydankids.com/uye/giris')
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

    # cart_cleaner(driver)
    cart_cleaner(driver)

    category_links = get_categories_links()

    product_links = get_product_links(category_links, driver)

    with open(f"zeydankids {date}.csv", "w", encoding='utf-8') as w_file:
        w_file.write("url|K1|K2|Name|Price 1|Price 2|Açıklama|BEDEN SEÇİNİZ|BİRİM ( 1 Adet ) FİYATI|"
                     "Brand|Code|Count|Paket Adedi|PAKET FİYATI ( 4 Adet )|"
                     "PAKET SAYISI SEÇİNİZ|Ürün Açıklaması|Ürün Detayları|Ürün Kodu|"
                     "Yaş Grubu|Size|IMGs|Renkle|IMG 1|IMG 2|IMG 3|IMG 4|IMG 5|"
                     "IMG 6|IMG 7|IMG 8|IMG 9|IMG 10|IMG 11|IMG 12|"
                     "IMG 13|IMG 14|IMG 15|Renk 1|Renk 2|Renk 3|"
                     "Renk 4|Renk 5|Renk 6|Renk 7|Renk 8|Renk 9|Renk 10|"
                     "Renk 11|Renk 12|Renk 13|Renk 14|Renk 15|sezon|checker" + '\n')

    with open(f"zeydankids {date}.csv", "a", encoding='utf-8') as w_file:
        get_product_data(product_links, driver, w_file)

    read_file = pd.read_csv(f"zeydankids {date}.csv", sep='|')
    read_file.to_excel(f"zeydankids {date}.xlsx", index=False)

main()