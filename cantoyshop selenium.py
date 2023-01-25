import csv
import datetime
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import pandas as pd
from bs4 import BeautifulSoup

# email
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

e = datetime.datetime.now()
startTime = datetime.datetime.now()

import glob

request_count = 20

date = f"{'%s.%s.%s %s-%s-%s' % (e.day, e.month, e.year, e.hour, e.minute, e.second)}"

product_url = []
# sex
K1 = []
#category
K2 = []
name = " "
price_1 = " "
price2 = " "
#description
aciklama = " "
#size
beden_seciniz = " "
#1_product_price
birim = " "
brand = " "
code = " "
count = " "
# 1_packet_quantity
paket_adedi = " "
# 1_packet_price
paket_fiyati = " "
#packet_quantity
paket_sayisi_seciniz = " "
#product_description
urun_aciklama = " "
#product_details
urun_detaylari = " "
#product_code
urun_kodu = " "
#age_group
yas_grubu = " "
#size
size = " "
#imgs
imgs_list = []
imgs = []
#color
renkle = []
renkle_list = []
img_1 = []
img_2 = []
img_3 = []
img_4 = []
img_5 = []
img_6 = []
img_7 = []
img_8 = []
img_9 = []
img_10 = []
img_11 = []
img_12 = []
img_13 = []
img_14 = []
img_15 = []
#color
renk_1 = []
renk_2 = []
renk_3 = []
renk_4 = []
renk_5 = []
renk_6 = []
renk_7 = []
renk_8 = []
renk_9 = []
renk_10 = []
renk_11 = []
renk_12 = []
renk_13 = []
renk_14 = []
renk_15 = []
#sezon
sezon = " "
checker = ""
err = ""
K2_old = ""

list_of_all_category = []
category_detail = []
all_category_urls_little = []
all_category_urls_main = []
product_links = []

def get_main_categories(driver: webdriver) -> list[BeautifulSoup]:
    r = driver.get("https://www.cantoyshop.com")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "left.pl15.pr15.col-sm-w100.col-sm-bb1.col-sm-bc3.drop.pos-r.pt15.pb15.col-sm-pt5.col-sm-pb5.col-sm-pos-r.menu-item.ana-menu-item")))
    # get pack of all categories in every section(in ERKEK, in KIZ...)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    main_categories = soup.find_all("li", class_="left pl15 pr15 col-sm-w100 col-sm-bb1 col-sm-bc3 drop pos-r pt15 pb15 col-sm-pt5 col-sm-pb5 col-sm-pos-r menu-item ana-menu-item")
    special_main_category = soup.find("li", class_="left pl15 pr15 col-sm-pl0 col-sm-pr0 col-sm-pt0 col-sm-pb0 col-sm-w100 col-sm-bb1 col-sm-bc3 drop pt8 pb8 col-sm-pos-r menu-item ana-menu-item col-sm-b-white col-sm-b-ra10 col-sm-mt10 col-sm-br0 babydolaContent pos-r")
    main_categories.append(special_main_category)
    for main_category in main_categories:
        list_of_all_category.append(main_category)
    # print(list_of_all_category)
    return list_of_all_category

def get_categories(list_of_all_category: list[BeautifulSoup], driver: webdriver) -> None:
    #get name of main category(ERKEK, KIZ...), link and name of every little category
    for main_category in list_of_all_category:
        all_category_urls_little = []
        # main_category_title
        K1 = main_category.find("span", class_="ceviri_def").text
        all_category_urls_little.append(K1)
        categories = main_category.find_all("a", class_="wi left text p10 ghostButton col-sm-bn col-sm-pt5 col-sm-pb5 ellipsis")
        for i in categories:
            category_url = i.get('href')
            all_category_urls_little.append(category_url)
        all_category_urls_main.append(all_category_urls_little)
    for i in all_category_urls_main:
        K1 = i[0]
        # print("title:", K1)
        #go to page with products in every category
        for j in range(1, len(i)):
            driver.get(i[j])
            soup = BeautifulSoup(driver.page_source, features="html.parser")
            a = True
            n = 2
            while a == True:
                try:
                    if soup.find("h4", class_="p0 t-center fw7 text center-w col-sm-fs14") or soup.find("h4", class_="m0 p0 t-center fw7 text"):
                        a = False
                    print(driver.current_url)
                    get_product_links(soup, K1, driver)
                    r = driver.get(i[j]+"?&sayfa="+str(n))
                    WebDriverWait(driver, 15).until(EC.presence_of_element_located(
                        (By.CLASS_NAME, "p0.pos-r.owh.z16")))
                    n += 1
                    soup = BeautifulSoup(driver.page_source, features="html.parser")
                except Exception as e:
                    print("Get end page:", e)
                    a = False


def get_product_links(soup: BeautifulSoup, K1: str, driver: webdriver) -> None:
    product_links = []
    K1 = K1
    #get item link
    product_links_on_page = soup.find_all("div", class_="p0 pos-r owh z16")
    for url in product_links_on_page:
        product_link = url.a.get('href')
        product_links.append(product_link)
        print(product_link)
    product_links_checker(product_links, K1, driver)


def product_links_checker(product_links: list, K1: str, driver: webdriver) -> None:
    for product_link in product_links:
        try:
            print("Getting details:")
            product_details_get(product_link, K1, driver)
        except Exception as e:
            print(e)
    cart_cleaner(driver)


def product_details_get(product_link: str, K1: str, driver: webdriver) -> None:
        K1 = K1
        try:
            # ram = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
            # print('!!!', ram)
            # ram_list.append(ram)
            driver.get(product_link)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ha.p0.lh22.fs16.fw8.bn.on.bsn.back-none.form-control.t-center.col-sm-fs14.text")))
            soup = BeautifulSoup(driver.page_source, features="html.parser")
            product_url = driver.current_url
            count_field = driver.find_element(By.CLASS_NAME, 'ha.p0.lh22.fs16.fw8.bn.on.bsn.back-none.form-control.t-center.col-sm-fs14.text')
            count_field.send_keys('1000')
            count_field.send_keys(Keys.ENTER)
            # driver.find_element(By.CLASS_NAME, 'cartButton.success-bg.white.lh40.b-ra5.nowrap.fs14.w100.col-sm-pl0.col-sm-pr0.bn.on.bsn.col-sm-white.col-sm-bt0.col-sm-bb0.op7.op-hover').click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "sweet-alert.showSweetAlert.visible")))
            count_text = driver.find_element(By.CLASS_NAME, 'sweet-alert.showSweetAlert.visible').text
            if 'Stok nedeniyle ekleme yapılamıyor' in count_text:
                checker = 0
            else:
                checker = count_text.split('yerine ')[1].split(' adet')[0]
            print(checker)
            name = soup.find("div", class_="col-12 fw7 text op8 fs20 lh20 mt5").text.strip()
            K2 = soup.find("div", class_="categoryName fw6 mt15 fs16 lh16 text op5 col-sm-mt0").find("span", class_="ceviri_def").text
            K2_old = K2
            K1 = "CAT " + K1 + " - " + K2
            price = soup.find("div", class_="fiyat fw7 fs30 lh30 col-sm-fs20").text.strip().replace(" ", "").replace("₺","").split("\n")[0]
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
                imgs_list.append(img.get("src"))
            imgs = "; ".join(imgs_list)
            imgs_row=[img_1,img_2,img_3,img_4,img_5,img_6,img_7,img_8,img_9,img_10,img_11,img_12,img_13,img_14,img_15]
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
            renkle_row = [renk_1, renk_2, renk_3, renk_4, renk_5, renk_6, renk_7, renk_8, renk_9, renk_10, renk_11, renk_12, renk_13, renk_14, renk_15]
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
            row = f"{product_url}#{K1}#{K2}#{name}#{price}#{price2}#{aciklama}#{beden_seciniz}#{birim}#{brand}" \
                  f"#{code}#{count}#{paket_adedi}#{paket_fiyati}#{paket_sayisi_seciniz}#{urun_aciklama}#{urun_detaylari}#{urun_kodu}" \
                  f"#{yas_grubu}#{size}#{imgs}#{renkle}#{'#'.join(imgs_row)}#{'#'.join(renkle_row)}#{sezon}#{checker}"
            print(row)
            if int(checker) >= request_count and not 'MAYA-01 MEVLÜT TAKIM' in row:
                with open(f"cantoyshop {date}.csv", mode="a", encoding='utf-8') as w_file:
                    file_writer = csv.writer(w_file, delimiter="^", lineterminator="\r")
                    write_row = row.split("#")
                    if write_row[0] != '' and write_row[1] != '' and write_row[2] != '' and write_row[3] != '':
                        if len(write_row) > 40:
                            file_writer.writerow(write_row)
                        else:
                            print(write_row)
                    w_file.close()
            else:
                print('Мало товара')
        except Exception as e:
            print(product_link)

def cart_cleaner(driver: webdriver) -> None:
    driver.get('https://www.cantoyshop.com/site/sepetim')
    links = driver.find_elements(By.CLASS_NAME, 'deleteContent.minLine.soft-slow.min')
    delete_urls = []
    for link in links:
        delete_urls.append(link.get_attribute('href'))
    for link in delete_urls:
        driver.get(link)

def main() -> None:
    with open(f"cantoyshop {date}.csv", mode="w", encoding='utf-8') as w_file:
        file_writer = csv.writer(w_file, delimiter="^", lineterminator="\r")
        file_writer.writerow(["url", "K1", "K2", "Name", "Price 1", "Price 2", "Açıklama", "BEDEN SEÇİNİZ",
                              "BİRİM ( 1 Adet ) FİYATI", "Brand", "Code", "Count", "Paket Adedi", "PAKET FİYATI ( 4 Adet )",
                              "PAKET SAYISI SEÇİNİZ", "Ürün Açıklaması", "Ürün Detayları", "Ürün Kodu", "Yaş Grubu",
                              "Size", "IMGs", "Renkle", "IMG 1", "IMG 2", "IMG 3", "IMG 4",
                              "IMG 5", "IMG 6", "IMG 7", "IMG 8", "IMG 9", "IMG 10", "IMG 11",
                              "IMG 12", "IMG 13", "IMG 14", "IMG 15", "Renk 1", "Renk 2", "Renk 3",
                              "Renk 4", "Renk 5", "Renk 6", "Renk 7", "Renk 8", "Renk 9", "Renk 10",
                              "Renk 11", "Renk 12", "Renk 13", "Renk 14", "Renk 15", "sezon", "checker"])
        w_file.close()
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
    #options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--window-size=1024,720")
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.cantoyshop.com/uye/giris')
    login = driver.find_element(By.ID, 'e_email')
    login.clear()
    login.send_keys('rafik1999@inbox.ru')
    time.sleep(2)
    password = driver.find_element(By.ID, 'e_sifre')
    password.clear()
    password.send_keys('300878raf')
    time.sleep(2)
    password.send_keys(Keys.ENTER)
    cart_cleaner(driver)
    get_main_categories(driver)
    get_categories(list_of_all_category, driver)

    read_file = pd.read_csv(f"cantoyshop {date}.csv", sep='^', engine='python')
    read_file.to_excel(f"cantoyshop {date}.xlsx", index=False, header=True)

def send_results() -> None:
    subject = "Обновление ассортимента Cantoyshop"
    body = "Обновление ассортимента Cantoyshop"
    sender_email = "почта_с_которой_отправляется@mail.ru"
    receiver_email = "почта_на_которую_отправляется@mail.ru"
    password = "пароль_почты_с_которой_отправляется"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email

    message.attach(MIMEText(body, "plain"))

    filename = f"{glob.glob('cantoyshop*.xlsx')[0]}"

    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename.replace(' ', '_')}",
    )

    message.attach(part)
    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.mail.ru", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


if __name__ == '__main__':
    main()
    send_results()

    print(datetime.now() - startTime)