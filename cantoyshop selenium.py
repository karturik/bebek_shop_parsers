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
for objects in tqdm(my_bucket.objects.filter(Prefix="Prefix/")):
    object_keys.append(objects.key)

def upload_image_to_s3(img_url) -> str:
    global object_keys
    file_name = img_url.replace('https://resimler/', '')
    key = f'parsing_data/{file_name}'
    if key in object_keys:
        print('Already exist photo')
        pass
    else:
        r = requests.get(img_url, stream=True)
        print('No such photo, upload')
        s3_client.put_object(
            Body=r.content,
            Bucket='Bucket',
            Key=f'parsing_data/{file_name}'
        )
    url = f'https://s3.eu-central-1.amazonaws.com/Bucket/parsing_data/{file_name}'
    return url


def get_categories_links():
    # driver.get("https://www.miniworld.com.tr/site/index")
    r = requests.get("https://www.cantoyshop.com/")
    soup = BeautifulSoup(r.content, features='html.parser')
    category_links = soup.find_all('a', class_='wi left text p10 ghostButton col-sm-bn col-sm-pt5 col-sm-pb5 ellipsis')
    category_links = set(link.get('href') for link in category_links)
    return category_links


def get_product_links(category_links):
    all_product_links = []
    for category_link in category_links:
        for i in range(1, 10):
            r = requests.get(category_link + f'?&sayfa={i}')
            soup = BeautifulSoup(r.content, features='html.parser')
            product_links = soup.find_all('a', class_='text bn on bsn elipsis')
            if product_links:
                all_product_links += list(link.get('href') for link in product_links)
            else:
                break

    all_product_links = list(set(all_product_links))
    print('Всего товаров найдено: ', len(all_product_links))
    return all_product_links


def cart_cleaner(driver):
    print('Чистим корзину...')
    driver.get('https://www.cantoyshop.com/site/sepetim')
    delete_urls = []
    links = driver.find_elements(By.CLASS_NAME, 'deleteContent.minLine.soft-slow.min')
    for link in links:
        delete_urls.append(link.get_attribute('href'))
    for link in delete_urls:
        driver.get(link)


def change_new_category(K2, name, K1):
    K2_new = K2
    if 'ERKEK' in K1.upper() or 'ERKEK' in K2.upper():
        if re.search(r"\b" + re.escape('TISORT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('TISORT') + r"\b", name.upper()) or re.search(r"\b" + re.escape('TİŞÖRT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('TİŞÖRT') + r"\b", name.upper()):
            K2_new = 'FUTBOLKI'
        elif re.search(r"\b" + re.escape('TEKALT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('TEKALT') + r"\b", name.upper()) or re.search(r"\b" + re.escape('TEK ALT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('TEK ALT') + r"\b", name.upper()):
            K2_new = 'BRUKI'
        elif re.search(r"\b" + re.escape('ŞORT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ŞORT') + r"\b", name.upper()):
            K2_new = 'SHORTY'
        elif re.search(r"\b" + re.escape('PANTALON') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('PANTALON') + r"\b", name.upper()):
            K2_new = 'DZHINSY'

    elif 'KIZ' in K1.upper() or 'KIZ' in K2.upper():
        if re.search(r"\b" + re.escape('BADI') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('BADI') + r"\b", name.upper()) or re.search(r"\b" + re.escape('TISORT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('TISORT') + r"\b", name.upper()) or re.search(r"\b" + re.escape('TİŞÖRT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('TİŞÖRT') + r"\b", name.upper()):
            K2_new = 'FUTBOLKI'
        elif re.search(r"\b" + re.escape('PANTOLON') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('PANTOLON') + r"\b", name.upper()):
            K2_new = 'BRUKI'
        elif re.search(r"\b" + re.escape('ŞORT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ŞORT') + r"\b", name.upper()):
            K2_new = 'SHORTY'
        elif re.search(r"\b" + re.escape('TAYT') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('TAYT') + r"\b", name.upper()):
            K2_new = 'LOSINI'
        elif re.search(r"\b" + re.escape('ELBİSE') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ELBİSE') + r"\b", name.upper()) or re.search(r"\b" + re.escape('ELBISE') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ELBISE') + r"\b", name.upper()) or re.search(r"\b" + re.escape('TAKIM') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('TAKIM') + r"\b", name.upper()):
            K2_new = 'PLATJA'
        elif re.search(r"\b" + re.escape('ETEK') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ETEK') + r"\b", name.upper()) or re.search(r"\b" + re.escape('ELBİSE-ETEK') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ELBİSE-ETEK') + r"\b", name.upper()):
            K2_new = 'JUBKI'

    elif 'BEBE' in K1.upper() or 'BEBE' in K2.upper():
        if re.search(r"\b" + re.escape('K.CORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('K.CORAP') + r"\b", name.upper()):
            K2_new = 'KOLGOTKI'
        elif re.search(r"\b" + re.escape('CORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('CORAP') + r"\b", name.upper()) or re.search(r"\b" + re.escape('ÇORAP') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('ÇORAP') + r"\b", name.upper()):
            K2_new = 'NOSKI'
        elif re.search(r"\b" + re.escape('PATIK') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('PATIK') + r"\b", name.upper()) or re.search(r"\b" + re.escape('PATİK') + r"\b", K2.upper()) or re.search(r"\b" + re.escape('PATİK') + r"\b", name.upper()):
            K2_new = 'PINETKI'
    return K2_new


def get_product_data(product_links, driver, w_file):
    for product_link in tqdm(product_links):
        try:
            if product_links.index(product_link) % 50 == 0:
                cart_cleaner(driver)
            driver.get(product_link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ha.p0.lh22.fs16.fw8.bn.on.bsn.back-none.form-control.t-center.col-sm-fs14.text")))
            soup = BeautifulSoup(driver.page_source, features="html.parser")
            product_url = driver.current_url
            try:
                count_field = driver.find_element(By.CLASS_NAME, 'ha.p0.lh22.fs16.fw8.bn.on.bsn.back-none.form-control.t-center.col-sm-fs14.text')
                count_field.send_keys('1000')
                count_field.send_keys(Keys.ENTER)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "sweet-alert.showSweetAlert.visible")))
                count_text = driver.find_element(By.CLASS_NAME, 'sweet-alert.showSweetAlert.visible').text
                if 'Stok nedeniyle ekleme yapılamıyor' in count_text:
                    checker = 0
                else:
                    checker = count_text.split('yerine ')[1].split(' adet')[0]
                print(checker)
            except:
                checker = 0
            if int(checker) >= request_count:
                K1 = soup.find_all('a', class_='black op5 left lh12 wi')[1].find('span', class_='ceviri_def').text
                name = soup.find("div", class_="col-12 fw7 text op8 fs20 lh20 mt5").text.strip()
                K2 = soup.find("div", class_="categoryName fw6 mt15 fs16 lh16 text op5 col-sm-mt0").find("span", class_="ceviri_def").text
                K2 = change_new_category(K2, name, K1)
                K1 = "CAT " + K1 + " - " + K2
                price = soup.find("div", class_="fiyat fw7 fs30 lh30 col-sm-fs20").text.strip().replace(" ", "").replace(",", ".").replace("₺","").split("\n")[0]
                # print(price)
                price2 = "-"
                paket_adedi = soup.find("div", class_="col-4 col-lg-4 pt10 br1 bc1").find_all("span", class_="op8")[1].text.strip().split("\n")[0].strip()
                # print(paket_adedi)
                urun_kodu = "CAT-" + name.replace('MİSS ', 'MİSS-').split(" ")[0]
                # print(urun_kodu)
                brand = name.split(" ")[0].split("-")[0]
                try:
                    size = soup.find_all("div", class_="col-4 col-lg-4 pb10 bb1 br1 bc1")[1].find_all("span", class_="op8")[1].text.strip().split("\n")[0]
                except Exception as e:
                    size = ""
                # print(yas_grubu)
                imgs_list = []
                for img in soup.find_all("img", class_="img-fluid col-sm-w100 col-sm-table col-sm-fn col-sm-ma"):
                    imgs_list.append(upload_image_to_s3(img.get("src")))
                imgs = "; ".join(imgs_list)
                imgs_row = list([] for i in range(1, 16))
                for x in range(0, 15):
                    try:
                        imgs_row[x] = imgs_list[x]
                    except Exception as e:
                        imgs_row[x] = " "
                renkle_list = []
                renkle = soup.find_all("span", class_="t-center text fs12 lh12 pt3 pb3 t-center block fw7 mt5")
                for renk in renkle:
                    if len(renk.text.strip()) > 2 and not 'model' in renk.text.strip().lower():
                        renk = renk.text.strip()
                        renkle_list.append(renk)
                    else:
                        renk = ""
                        renkle_list.append(renk)

                if len(renkle_list) > 0:
                    renkle = "; ".join(renkle_list)
                else:
                    renkle = ""
                # print(renkle)
                renkle_row = list([] for i in range(1, 16))
                for x in range(0, 15):
                    try:
                        if not 'model' in renkle_list[x].lower():
                            renkle_row[x] = renkle_list[x].capitalize()
                        else:
                            renkle_row[x] = ""
                    except Exception as e:
                        renkle_row[x] = ""
                if 'yaş' in renkle_row:
                    if size == "":
                        size = renkle_row
                        renkle_row = []
                    else:
                        renkle_row = []
                try:
                    sezon = soup.find("div", class_="fw7 text op8 fs14 block lh14 col-sm-fs12 col-sm-lh12").find_all("span", class_="op8")[1].text.strip().split("\n")[0]
                except:
                    sezon = ""
                # print(sezon)
                row = f"{product_url}#{K1}#{K2}#{name}#{price}#{price2}#{''}#{''}#{''}#{brand}" \
                      f"#{''}#{''}#{''}#{''}#{''}#{''}#{''}#{urun_kodu}" \
                      f"#{''}#{size}#{imgs}#{renkle}#{'#'.join(imgs_row)}#{'#'.join(renkle_row)}#{sezon}#{checker}"

                write_row = row.split("#")
                print(write_row)

                if not 'MAYA-01 MEVLÜT TAKIM' in row:
                    if write_row[0] != '' and write_row[1] != '' and write_row[2] != '' and write_row[3] != '':
                        if len(write_row) > 40:
                            w_file.write(row + '\n')
                        else:
                            print(write_row)
            else:
                print('Мало товара')
        except Exception as e:
            print(e)


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
    options.add_experimental_option('prefs', prefs)
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument('--blink-settings=imagesEnabled=false')
    # options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1024,720")
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    driver.get('https://www.cantoyshop.com/uye/giris')
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

    category_links = get_categories_links()

    product_links = get_product_links(category_links)

    with open(f"cantoyshop {date}.csv", "w", encoding='utf-8') as w_file:
        w_file.write("url#K1#K2#Name#Price 1#Price 2#Açıklama#BEDEN SEÇİNİZ#BİRİM ( 1 Adet ) FİYATI#"
                     "Brand#Code#Count#Paket Adedi#PAKET FİYATI ( 4 Adet )#"
                     "PAKET SAYISI SEÇİNİZ#Ürün Açıklaması#Ürün Detayları#Ürün Kodu#"
                     "Yaş Grubu#Size#IMGs#Renkle#IMG 1#IMG 2#IMG 3#IMG 4#IMG 5#"
                     "IMG 6#IMG 7#IMG 8#IMG 9#IMG 10#IMG 11#IMG 12#"
                     "IMG 13#IMG 14#IMG 15#Renk 1#Renk 2#Renk 3#"
                     "Renk 4#Renk 5#Renk 6#Renk 7#Renk 8#Renk 9#Renk 10#"
                     "Renk 11#Renk 12#Renk 13#Renk 14#Renk 15#sezon#checker" + '\n')

    with open(f"cantoyshop {date}.csv", "a", encoding='utf-8') as w_file:
        get_product_data(product_links, driver, w_file)

    read_file = pd.read_csv(f"cantoyshop {date}.csv", sep='#')
    read_file.to_excel(f"cantoyshop {date}.xlsx", index=False)

main()
