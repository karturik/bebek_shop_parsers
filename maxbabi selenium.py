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

translate = {'слово': 'перевод', 'YENI': 'малыш', 'BOLERO': 'болеро', 'BANDI-PAPYON': 'Лента С галстуком', 'ŞAPKA-SAÇ': 'Шапка волосы', 'ÖNLÜK-MENDİL-ELDİVEN-EMZİK': 'Слюнявчик Платок Перчатки аксессуары младенцы', 'AYAKKABI-PAT-İK': 'Обувь Пинетки', 'HIRKA-YELEK-MONT': 'Кардиган Жилетка Куртка', 'AYAKKABI-BABET': 'Обувь BABET', 'CEKET-MONT-HIRKA': 'Пиджак Куртка Кардиган', 'KOZMONOT-MONT': 'КУРТКА С ПРИНТОМ', 'YELEK-HIRKA': 'Жилетка Кардиган', 'ZIBIN-HASTANE': 'Набор На выписку', 'ELBİSE-JİLE-ETEK': 'Платье Сарафан Юбка', 'ÖNLÜK-BERE-BANDANA': 'СЛЮНЯВЧИК ШАПКА ШАПКА', 'MONT-CEKET': 'КУРТКА ПИДЖАК', 'ITRİYAT-BANYO': 'ITRİYAT БАННЫЕ', 'AÇMA-BATTANİYE': 'ОТКРЫТИЕ ОДЕЯЛО', 'MONT-KOZMONOT': 'КУРТКА С ПРИНТОМ', 'AYAKKABI-PATİK-ÇORAP': 'Обувь Пинетки Носки', 'TAKIM-TULUM': 'Костюм Комбинезон', 'PANTOLON-TAYT-TEK': 'Брюки лосины Часть', 'ELBİSE-ETEK': 'Платье Юбка', 'GIRL': 'Девочка', 'BAYANLAR': 'Девочка', 'KIZ': 'Девочка', 'GIRLS': 'Девочка', '1-KIZ': 'Девочка', 'ERK': 'Мальчик', 'ER': 'ER', 'ERKEK': 'Мальчик', 'BOYS': 'Мальчик', '2-ERKEK': 'Мальчик', 'ERK.': 'Мальчик', 'KIZ/ERK': 'Девочка/Мальчик', 'UNİSEX': 'Девочка/Мальчик', 'UNISEX': 'Девочка/Мальчик', 'KISLIK': 'Зимний', 'KIŞ': 'Зимний', 'KIŞLIK': 'Зимний', 'KIS': 'Зимний', 'YAZLIK': 'Лето', 'YAZ': 'Лето', 'YAZILI': 'Лето', 'SUMMER': 'Лето', 'YAZI': 'Лето', 'MEVSIMLIK': 'Демисезонный', 'MEVS': 'Демисезонный', 'MEVSİM': 'Демисезонный', 'MEVSİMLİK': 'Демисезонный', '"MEVSIMLIK': 'Демисезонный', 'MEVLÜT': 'Крестильный костюм', 'MEVLUTLUK': 'Крестильный костюм', 'MEVLUT': 'Крестильный костюм', 'MEVLÜTLÜK': 'Крестильный костюм', 'AKSESUAR&MEND;İL&ÖNLÜK': 'Аксессуар', 'KOLYELI': 'Аксессуар', 'LAZIMLIK': 'аксессуары младенцы', 'SÜNGERİ': 'аксессуары младенцы', 'EMZİK': 'аксессуары младенцы', 'EMZİĞİ': 'аксессуары младенцы', 'MAŞRAPA': 'аксессуары младенцы', 'TAS': 'аксессуары младенцы', 'KAŞIYICI': 'аксессуары младенцы', 'TARAK': 'аксессуары младенцы', 'KÜVET': 'аксессуары младенцы', 'KRINKIL': 'аксессуары младенцы', 'EMZIK': 'аксессуары младенцы', 'OYUNCAKLAR': 'аксессуары младенцы', 'OYUNCAKLI': 'аксессуары младенцы', 'OYUNCAK': 'аксессуары младенцы', 'TK.(2AD)': 'Балетки', 'BLUZ': 'Блузка', 'BADİ': 'Боди', 'BADY': 'Боди', 'ASK.BADİ': 'Боди', 'BODY': 'Боди', 'BADI': 'Боди', 'BADİ(SWET': 'Боди', 'U.K.BADİ': 'Боди с длинным рукавом', 'BOXER': 'Боксеры', 'PANTOLON': 'Брюки', 'PANTALON': 'Брюки', 'PANT': 'Брюки', 'PANT.': 'Брюки', 'PANTOLON-TEK': 'Брюки', 'SÜTYENİ': 'Бюстгальтер', 'KOT': 'Джинсовый', 'PANTOLON(JEANS)': 'Джинсы', 'YAĞMURLUK': 'Дождевик', 'YAĞMURLUĞU': 'Дождевик', 'YAĞMUR': 'Дождевик', 'YAGMURLUK': 'Дождевик', 'MONT-KABAN-YAĞMURLUK': 'Дождевик', 'YELEK': 'Жилетка', '"YELEK': 'Жилетка', 'CAPRİ': 'Капри', 'KAPRİ': 'Капри', 'KAPRI': 'Капри', '"KAPRI': 'Капри', 'KAPRİ-ŞORT': 'Капри', 'HIRKA': 'Кардиган', '"HIRKA': 'Кардиган', 'TULUM': 'Комбинезон', 'TULUMU': 'Комбинезон', 'PRE.TULUM': 'Комбинезон', 'TULUMLAR': 'Комбинезон-штаны', 'TULUMLARI': 'Комбинезон-штаны', 'ROMPER': 'Комбинезон с шортами', 'SLOPET': 'Комбинезон на лямках', 'SALOPET': 'Комбинезон на лямках', 'SALOPETLER': 'Комбинезон на лямках', 'SALOPETLERİ': 'Комбинезон на лямках', 'SLOPETLI': 'Комбинезон на лямках', 'KUNDAK': 'Конверт', 'KUNDAKLAR': 'Конверт', 'KUNDAK-GREY': 'Конверт', 'KUNDAK-ECRU': 'Конверт', 'KUNDUZ': 'Конверт', 'KUNDAK1233': 'Конверт', 'KUNDAK-MIX': 'Конверт', 'KUNDAK904': 'Конверт', 'KUNDAK-PİNK': 'Конверт', 'KUNDAK-ŞAPKA': 'Конверт', 'KUNDAK-SALMON': 'Конверт', 'KUNDAK103': 'Конверт', 'KUNDAK424': 'Конверт', 'KUNDAK-OLİVEDRAB': 'Конверт', 'KUNDAK-POWDER': 'Конверт', 'KUNDAK329': 'Конверт', 'KUNDAK480': 'Конверт', 'KUNDAK-BROWN': 'Конверт', 'KUNDAK-MİX': 'Конверт', 'KUNDAK-YELLOW': 'Конверт', 'KUNDAK-DARKBLUE': 'Конверт', 'KUNDAK-DARKGREY': 'Конверт', 'TAKIM': 'Костюм', 'TK': 'Костюм', 'TAKIMI': 'Костюм', 'TKM': 'Костюм', 'TK.': 'Костюм', 'TAKIMI.': 'Костюм', 'TKM.': 'Костюм', 'TAKIMLAR': 'Костюм', 'TAKIM(9-12-18AY)': 'Костюм Малыш', 'MONT': 'Куртка', '"MONT': 'Куртка', 'TAYT': 'лосины', 'ATLET': 'Майка', 'ÇORAP': 'Носки', 'ÇORABI': 'Носки', 'CORAP': 'Носки', 'AYAKKABI': 'Обувь', 'AYAKKABI+SAÇ': 'обувь + для волос', 'GİYİM': 'Одежда', 'KIYAFET': 'Одежда', 'GIYIM': 'Одежда', 'YORGAN': 'Одеяло', 'BATANİYE': 'Одеяло', 'BATTANİYE': 'Одеяло', 'BATTANIYE': 'Одеяло', 'KABAN': 'Пальто', 'ELDİVEN': 'Перчатки', 'ELDIVEN': 'Перчатки', 'CEKET': 'Пиджак', 'SMOKIN': 'Пиджак', 'ÇEKET': 'Пиджак', 'PİJAMA': 'Пижама', 'PIJAMA': 'Пижама', 'B.PİJAMA': 'Пижама', 'PJM': 'Пижама', 'Ç.PİJAMA': 'Пижама', 'PİJAMALAR': 'Пижама', 'PİJAMALARI': 'Пижама', 'PATİK': 'Пинетки', 'PATİKLİ': 'Пинетки', 'PATIKLI': 'Пинетки', 'PATIK': 'Пинетки', 'PATİĞİ': 'Пинетки', 'ELBİSE': 'Платье', 'ELBISE': 'Платье', 'ALTAÇMA': 'Плед', 'ÖRTÜSÜ': 'Плед', 'EKOSELI': 'Плед', 'YASTIK': 'Подушка', 'YASTIĞI': 'Подушка', 'MİNDERİ': 'Подушка', 'HAVLU': 'Полотенце', 'HAVLUSU': 'Полотенце', 'HAVLULAR': 'Полотенце', 'GRUBU-HAVLU': 'Полотенце', 'BORNOZ-HAVLU': 'Полотенце','HAVLU-BORNOZ': 'Полотенце', 'NEVRESİM-KUTU': 'Постельное', 'YATAK': 'Постельное', 'GÖMLEK': 'Рубашка', 'GOMLEK': 'Рубашка', '"GÖMLEK': 'Рубашка', 'SHIRT': 'Рубашка(футболка)', 'CANTA': 'Рюкзак', 'JİLE': 'Сарафан', 'JILE': 'Сарафан', 'DAMATLIK': 'Свадебный костюм', 'GELİNLİK': 'Свадебный наряд', 'SWEAT': 'Свитшот', 'T-SHIRT-SWEAT': 'Свитшот', 'KAZAK': 'Свитер', 'SÜVETER': 'Свитер', '"SÜVETER': 'Свитер', 'SWIT': 'Свитер', 'SWEATSHİRT': 'Свитшот', 'SWEATSHIRT': 'Свитшот', 'ÖNLÜK': 'Слюнявчик', 'ONLUK': 'Слюнявчик', 'ÖNLÜĞÜ': 'Слюнявчик', 'ONLUK-MENDİL': 'Слюнявчик', 'ESOFMAN': 'Спортивный костюм', 'EŞOFMAN': 'Спортивный костюм', 'TORBA': 'Сумка', 'ÇANTA': 'Сумка', 'ÇANTASI': 'Сумка', 'KULOTU': 'Трусики', 'KULOTLU': 'Трусики', 'KÜLODU': 'Трусики', 'KÜLOT': 'Трусики', 'KULODU': 'Трусики', 'KİLOD': 'Трусики', 'KILOT': 'Трусики', 'TUNİK': 'Туника', 'TUNIK': 'Туника', 'TİŞÖRT': 'Футболка', 'TSHIRT': 'Футболка', 'T-SHIRT': 'Футболка', 'T-SHİRT': 'Футболка', 'SHİRT': 'Футболка', 'TISORT': 'Футболка', 'TIŞÖRT': 'Футболка', 'TSHİRT': 'Футболка', 'TŞHRT': 'Футболка', 'SHIRT)': 'Футболка', 'TİŞÖRT/GÖMLEK/SWEAT': 'Футболка', 'BORNOZ': 'Халаты', 'DIZALTI': 'Чулки', 'ŞAPKA': 'Шапка', 'ŞAPKA-BERE': 'Шапка', 'BERE': 'Шапка', 'SAPKA': 'Шапка', 'BANDANA': 'Шапка', 'ŞAPKA-BANDANA': 'Шапка', 'ŞAPKASI': 'Шапка', '"BERE': 'Шапка', '"BANDANA': 'Шапка', 'BANDANALI': 'Шапка', 'FULARLI': 'Шарф', 'FULAR': 'Шарф', 'ATKI': 'Шарф', '"ATKI': 'Шарф', 'ŞORT': 'Шорты', 'SHORT': 'Шорты', 'SORT': 'Шорты', 'TEK': 'Часть', 'TEKALT': 'Штаны', 'ŞALVAR': 'Штаны', 'tek alt': 'Штаны', 'ALT-TEK': 'Штаны', 'JOGGER': 'штаны джоггеры', 'SALVARLI': 'штаны шаровары', 'ETEK': 'Юбка', 'ETEGI': 'Юбка', 'ETEĞİ': 'Юбка', 'KADİFE': 'Бархат', 'KADIFE': 'Бархат', 'KADIFELI': 'Бархат', 'WELSOFT': 'Велсофт', 'WELSOFTLU': 'Велсофт', 'VELSOFLU': 'Велсофт', 'VELSOFT': 'Велсофт', 'PELUŞ': 'Велсофт', 'VELSOFTLU': 'Велсофт', 'WELSOF': 'Велсофт', 'TRİKO-WELSOFT': 'Велсофт', 'VISKON': 'Вискоза', 'ÖRME': 'Вязанные', 'İPLİK': 'Вязанные', 'ORGU': 'Вязанные', 'ORGULU': 'Вязанные', 'SAÇÖRGÜ': 'Вязанные', 'ÖRGÜLÜ': 'Вязанные', 'ÖRGÜ': 'Вязанные', 'GABARDIN': 'Габардин', 'JAKAR': 'Жаккард', 'JAKARLI': 'Жаккард', 'İNTERLOK': 'Интерлок', 'INTERLOK': 'Интерлок', 'DERİ': 'Кожанный', 'DERILI': 'Кожаный', 'DANTELLI': 'Кружево', 'DANTELLİ': 'Кружево', 'DANTEL': 'Кружево', 'TÜL': 'Кружево', 'TULLU': 'Кружево', 'BRODE': 'Кружево', 'OYALI': 'Кружево', 'GUPURLU': 'Кружево', 'VELBOA': 'Меховой', 'FLUFFY': 'Меховой', 'MÜSLİN': 'Муслин', 'MÜSLİNLİ': 'Муслин', 'MUSLİN': 'Муслин', 'MÜSLIN': 'Муслин', 'SATEN': 'Сатен', 'DOKUMA': 'Текстиль', 'TRIKO': 'Трикотаж', 'TRİKO': 'Трикотаж', 'TRIKOLU': 'Трикотаж', 'RİBANA': 'Трикотаж', 'RİBANALI': 'Трикотаж', 'RBN': 'Трикотаж', 'SELANIK': 'Трикотаж', 'PAZEN': 'Фланель', 'PENYELİ': 'Хлопок', 'PENYE': 'Хлопок', 'PAMUKLU': 'Хлопок', 'PAMUK': 'Хлопок', 'PENYELI': 'Хлопок', 'KETEN': 'Шерсть', 'KURKLU': 'Шерсть', 'ÇAMAŞIR': 'Шерсть', 'LIKRALI': 'Эластан', 'LİKRA': 'Эластан', 'LİKRALI': 'Эластан', 'ELASTEN': 'Эластан', 'LASTİKLİ': 'Эластан', 'LIKRA': 'Эластан', 'LYC': 'Эластан', '/': '/', '0': '0', 'SIFIR': '0', '1': '1', 'IKILI': '1', 'İKİLİ': '2', 'IKI': '2', 'CIFT': '2', 'İKİ': '2', 'ÇİFT': '2', '2': '2', 'İKILI': '2', 'ÇIFT': '2', 'İKI': '2', 'UC': '3', '3': '3', 'ÜÇ': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', 'B': '8', '9': '9', '10': '10', '12': '12', '15': '15', '2İP': '2 Нитки', '2IP': '2 Нитки', 'İKİİP': '2 нитки', '2LI': '2 шт', '2Lİ': '2 шт', "2'Lİ": '2 шт', '2’LI': '2 шт', 'ÜÇIP': '3 нитки', 'ÜÇİP': '3 нитки', 'ÜÇLÜ': '3 шт', '8Lİ': '8 шт', 'SÜPERMİNİ': 'SÜPERMİNİ', 'AKSESUAR': 'Аксессуар', 'BALERO': 'Болеро', 'BANYO': 'Банные', 'KOLSUZ': 'Без рукавов', 'PATİKSİZ': 'без пинеток', 'BEYAZ': 'Белый', 'SIMLI': 'Блестящий', 'BÜYÜK': 'Большой', 'BUYUK': 'Большой', 'PUANLI': 'В горошек', 'NOHUTLU': 'В горошек', 'NOHUT': 'В горошек', 'NOKTALI': 'В горошек', 'EKOSE': 'В клетку', 'EKOSELİ': 'В клетку', 'KARE': 'В клетку', 'KARELİ': 'В клетку', 'KUTULU': 'В коробке', 'KUTU': 'В коробке', 'ÜST': 'Верх', 'İÇ': 'Внутренняя', 'FIRFIRLI': 'воланы', 'SAÇ': 'волосы', 'SAC': 'волосы', 'YAKASI': 'Вороткик', 'YAKA': 'Воротник', 'ÇIKIŞI': 'Выписку', 'ÇIKIŞLARI': 'Выписку', 'İPLIK': 'Вязанные', 'GABARDİN': 'Габардин', 'EMZİRME': 'грудное кормление', 'GRUBU': 'Группа', 'KRUVAZE': 'Двубортный', 'UZUN': 'Длинный', 'U.': 'Длинный', 'UZUNKOL': 'Длинный рукав', 'KARELI': 'Закрытый', 'BİLEKTE': 'Запястье', 'VE': 'и', '&': 'и', 'AND': 'и', 'KAMUFLAJ': 'Камуфляж', 'KLASIK': 'Классический', 'KLASİK': 'Классический', 'DÜĞME': 'Кнопка', 'DERI': 'Кожаный', 'DIZ': 'Колено', '"BEŞIK': 'Колыбель', 'KOMANDO': 'Команда', 'TEAM': 'Команда', 'KOMPAK': 'Компактный', 'KISA': 'Короткий', 'KISAKOL': 'Короткий рукав', 'YARIMKOL': 'Короткий рукав', 'GÜZEL': 'Красивая', 'DANTELI': 'Кружево', 'LAKOS': 'Лакост', 'LAKOST': 'Лакост', 'BANDI': 'Лента', 'LÜKS': 'Люкс', 'PREMIUM': 'Люкс', 'LÜX': 'Люкс', 'LUX': 'Люкс', 'LUKS': 'Люкс', 'KÜÇÜK': 'Маленький', 'MİNİK': 'Маленький', 'KUCUK': 'Маленький', 'MINIK': 'Маленький', 'MIKRO': 'Микро', 'MINI': 'Мини', 'MİNİ': 'Мини', 'MOBIL': 'Мобильная', 'FASHION': 'мода', 'MUSLIN': 'Муслин', 'HASTANE': 'На выписку', 'ASKILI': 'на лямках', 'SET': 'Набор', 'ZIBIN': 'Набор', 'SETİ': 'Набор', 'SET-ECRU': 'Набор', 'SET-PİNK': 'Набор', 'SET-BROWN': 'Набор', 'SET-PLUM': 'Набор', 'SET-BLUE': 'Набор', 'SET-MİNTGREEN': 'Набор', 'SET-ROSE': 'Набор', 'SET-GREY': 'Набор', 'SET-YELLOW': 'Набор', 'SET-CLARED': 'Набор', 'SET-MINTGREEN': 'Набор', 'SET-POWDER': 'Набор', 'SET-MİNT': 'Набор', 'SET-NAVY': 'Набор', 'SET-IND.BLUE': 'Набор', 'SET-ARMYGREEN': 'Набор', 'SET-CLAREDRED': 'Набор', 'SET-BEIGE': 'Набор', 'SETI': 'Набор', '/ZIBIN': 'Набор', 'TAKIMLARI': 'Набор', 'SETLERI': 'Набор', 'SETLERİ': 'Набор', 'SISME': 'Надувная', 'ŞİŞME': 'Надувная', 'ŞIŞME': 'Надувной', 'PELERİN': 'Накидка', 'DİZLİĞİ': 'Наколенники', 'PREMATÜRE': 'Недоношенный', 'PREMATURE': 'Недоношенный', 'NEON': 'Неоновый', 'ALT': 'Нижнее', 'IP': 'Нитка', 'İP': 'Нитка', 'KABARTMA': 'Облегченный', 'SHOES)': 'Обувь', 'AYKKABI': 'Обувь', 'AYAKKABI-PATİK': 'Обувь', 'AÇMA': 'Открытие', 'ACMA': 'Открытие', 'ACIK': 'Открытый', 'GARSON': 'Официант', 'PAYET': 'Пайетки', 'PULLU': 'Пайетки', 'ÖN': 'Передний', 'MENDIL': 'Платок', 'ROBA': 'Плесированная', 'PILELI': 'Плесированная', 'ROBASI': 'Плесированная', 'ROBALI': 'Плесированная', 'PILISELI': 'Плесированная', 'PİLELİ': 'Плесированная', 'OMUZ': 'Плечо', 'UCU': 'по краю', 'ASKI': 'Подтяжки', 'POLO': 'Поло', 'YARIM': 'Половина', 'CIZGILI': 'Полосатый', 'ÇİZGİLİ': 'Полосатый', 'ÇİZGİ': 'Полосатый', 'SERITLI': 'Полосатый', 'ŞERİTLİ': 'Полосатый', 'YIPRATMA': 'Потёртое', 'SILIP': 'Потертый', 'YIPRATMALI': 'Потёртый', 'ABİYE': 'Праздничное', 'ÇEYİZ': 'Приданное', 'ÜRÜNLER': 'Продукты', 'SADE': 'Простой', 'DUZ': 'Прямой', 'DÜZ': 'Прямой', 'BOY': 'Размер', 'BEDEN': 'Размер', 'KOL': 'Рукав', 'KOLLAR': 'Рукав', 'KOLU': 'Рукав', 'KOLLARI': 'Рукав', 'K.': 'Рукав', 'AKSESUARLI': 'С аксесуаром', 'FIYONKLU': 'с бантом', 'FİYONKLU': 'с бантом', 'PELUŞLU': 'С бантом', 'FIYONK': 'С бантом', 'PAPYONLU': 'С бантом', 'PUSKULLU': 'с бахрамой', 'BADİLİ': 'С боди', 'BADILI': 'С боди', 'BOLEROLU': 'с болеро', 'PANTOLONLU': 'С брюками', 'BONCUKLU': 'С бусинкой', 'YAKALI': 'С воротником', 'NAKISLI': 'С вышивкой', 'NAKIŞLI': 'С вышивкой', 'NAKIŞ': 'С вышивкой', 'NAKIS': 'С вышивкой', 'NAKS': 'С вышивкой', 'NKS': 'С вышивкой', 'NAKSILI': 'С вышивкой', 'KRAVATLI': 'С галстуком', 'KRAVAT': 'С галстуком', 'PAPYON': 'С галстуком', 'KOTLU': 'С джинсами', 'INCILI': 'С жемчужиной', 'İNCİLİ': 'С жемчужиной', 'ARMULLU': 'С жемчужиной', 'INCI': 'С жемчужиной', 'İNCİ': 'С жемчужиной', 'İNCILI': 'С жемчужиной', 'YELEKLİ': 'С жилетом', 'YELEKLI': 'С жилетом', 'TASLI': 'С камнями', 'TAŞLI': 'С камнями', 'TAŞ': 'С камнями', 'KAPRILI': 'С капри', 'KAPŞONLU': 'С капюшоном', 'KAPSONLU': 'С капюшоном', 'KAPÜŞONLU': 'С капюшоном', 'HIRKALI': 'С кардиганом', 'CEPLI': 'С карманом', 'CEP': 'С карманом', 'CEPLİ': 'С карманом', 'DUGMELI': 'С кнопками', 'ÇITÇITLI': 'С кнопками', 'CITCITLI': 'С кнопками', 'DÜĞMELİ': 'С кнопками', 'DUGME': 'С кнопками', 'TULUMLU': 'С комбинезоном', 'KAPAKLI': 'С крышкой', 'CEKETLI': 'С курткой', 'KURDELELİ': 'С лентой', 'SERIT': 'С лентой', 'TAYTLI': 'С лосинами', 'MANSETLI': 'с манжетой', 'FERMUARLI': 'С молнией', 'FERMUAR': 'С молнией', 'COOL': 'С надписью', 'LOVE': 'С надписью', 'I': 'С надписью', 'ME': 'С надписью', 'THE': 'С надписью', 'MY': 'С надписью', 'HAPPY': 'С надписью', 'SEVIMLI': 'С надписью', 'CUTE': 'С надписью', 'YOU': 'С надписью', 'MELODY': 'С надписью', 'ONU': 'С надписью', 'SWEET': 'С надписью', 'ROCK': 'С надписью', 'SÜPER': 'С надписью', 'SUPER': 'С надписью', 'DREAM': 'С надписью', 'BE': 'С надписью', 'LİTTLE': 'С надписью', 'BEST': 'С надписью', 'MOM': 'С надписью', 'MAMA': 'С надписью', 'MOMMY': 'С надписью', 'DAD': 'С надписью', 'DADDY': 'С надписью', 'DONT': 'С надписью', 'LETS': 'С надписью', 'DIJITAL': 'С надписью', 'PARIS': 'С надписью', 'PLAY': 'С надписью', 'LITTLE': 'С надписью', 'POWER': 'С надписью', 'UP': 'С надписью', 'NEVER': 'С надписью', 'SHINE': 'С надписью', 'GOOD': 'С надписью', 'GO': 'С надписью', 'CLUB': 'С надписью', 'ROAR': 'С надписью', 'PRENSES': 'С надписью', 'PRINCESS': 'С надписью', 'LIFE': 'С надписью', 'OFF': 'С надписью', 'BOSS': 'С надписью', 'KING': 'С надписью', 'TIME': 'С надписью', 'STOP': 'С надписью', 'GAME': 'С надписью', 'SMILE': 'С надписью', 'MILK': 'С надписью', 'MİSS': 'С надписью', 'NEWYORK': 'С надписью', 'ANGEL': 'С надписью', 'MUSIC': 'С надписью', 'ÇORAPLI': 'С носками', 'ELDIVENLI': 'С перчатками', 'CEKETLİ': 'С пиджаком', 'ASTARLI': 'С подкладкой', 'PONPONLU': 'С помпоном', 'BASKILI': 'С принтом', 'BASKI': 'С принтом', 'BASK': 'С принтом', 'BASK.': 'С принтом', 'BSK': 'С принтом', 'BALONLU': 'С принтом', 'AYI': 'С принтом', 'AYILI': 'С принтом', 'AYICIKLI': 'С принтом', 'AYICIK': 'С принтом', 'BEAR': 'С принтом', 'PANDA': 'С принтом', 'PANDALI': 'С принтом', 'KOALA': 'С принтом', 'BUNNY': 'С принтом', 'TAVŞAN': 'С принтом', 'TAVŞANLI': 'С принтом', 'TAVSANLI': 'С принтом', 'YILDIZ': 'С принтом', 'YILDIZLI': 'С принтом', 'STAR': 'С принтом', 'KEDI': 'С принтом', 'KEDİ': 'С принтом', 'KEDİLİ': 'С принтом', 'KEDILI': 'С принтом', 'CAT': 'С принтом', 'KALP': 'С принтом', 'KALPLI': 'С принтом', 'KALPLİ': 'С принтом', 'ASLAN': 'С принтом', 'SOKET': 'С принтом', 'KELEBEK': 'С принтом', 'KELEBEKLİ': 'С принтом', 'KOPEK': 'С принтом', 'KÖPEK': 'С принтом', 'ARABA': 'С принтом', 'ARABALI': 'С принтом', 'KUZU': 'С принтом', 'FIL': 'С принтом', 'UNICORN': 'С принтом', 'MICKEY': 'С принтом', 'MIKI': 'С принтом', 'MINNIE': 'С принтом', 'BATMAN': 'С принтом', 'KANGURU': 'С принтом', 'ARMALI': 'С принтом', 'PENGUEN': 'С принтом', 'TAŞIMA': 'С принтом', 'LEOPAR': 'С принтом', 'DEFNE': 'С принтом', 'ARI': 'С принтом', 'KOZMONOT': 'С принтом', 'BALIK': 'С принтом', 'KAFA': 'С принтом', 'BAGLAMALI': 'С принтом', 'ZÜRAFA': 'С принтом', 'ZURAFA': 'С принтом', 'GOZLUKLU': 'С принтом', 'DINO': 'С принтом', 'KDF': 'С принтом', 'YAPRAK': 'С принтом', 'KURBAGA': 'С принтом', 'FILLI': 'С принтом', 'FİLLİ': 'С принтом', 'FİL': 'С принтом', 'ASLANLI': 'С принтом', 'DİNAZOR': 'С принтом', 'DİNO': 'С принтом', 'DINAZOR': 'С принтом', 'KAPLAN': 'С принтом', 'KUS': 'С принтом', 'ZEBRA': 'С принтом', 'ORDEK': 'С принтом', 'KARPUZ': 'С принтом', 'KARGO': 'С принтом', 'FLAMINGO': 'С принтом', 'TACLI': 'С принтом', 'TAC': 'С принтом', 'BULUT': 'С принтом', 'BULUTLU': 'С принтом', 'MAYMUN': 'С принтом', 'HAYVANLAR': 'С принтом', 'VENÜS': 'С принтом', 'KUŞ': 'С принтом', 'KUZULU': 'С принтом', 'CILEK': 'С принтом', 'BAKLAVA': 'С принтом', 'ANANAS': 'С принтом', 'BALON': 'С принтом', 'KİRAZLI': 'С принтом', 'CANAVAR': 'С принтом', 'BATIK': 'С принтом', 'MOUSE': 'С принтом', 'SAYILAR': 'С принтом', 'CIVCIV': 'С принтом', 'SKATE': 'С принтом', 'KIRAZLI': 'С принтом', 'KIRAZ': 'С принтом', 'KELEBEKLI': 'С принтом', 'BALİNA': 'С принтом', 'PALMIYE': 'С принтом', 'KOPEKLI': 'С принтом', 'KÖPEKLİ': 'С принтом', 'INEK': 'С принтом', 'TOP': 'С принтом', 'ÖRDEK': 'С принтом', 'MEYVE': 'С принтом', 'DENIZ': 'С принтом', 'TİMSAH': 'С принтом', 'GEMI': 'С принтом', 'KANATLI': 'С принтом', 'ŞEMSİYELİ': 'С принтом', 'HAYVAN': 'С принтом', 'TAÇLI': 'С принтом', 'YELKENLI': 'С принтом', 'DENIZCI': 'С принтом', 'DONDURMA': 'С принтом', 'ROBOT': 'С принтом', 'SINCAP': 'С принтом', 'BAYKUŞ': 'С принтом', 'DALMACYALI': 'С принтом', 'FARE': 'С принтом', 'ALTI': 'С принтом', 'KORSAN': 'С принтом', 'TREN': 'С принтом', 'BALIKLI': 'С принтом', 'ELMALI': 'С принтом', 'KOYUN': 'С принтом', 'TIGER': 'С принтом', 'RABBIT': 'С принтом', 'KUSLU': 'С принтом', 'SURF': 'С принтом', 'BIYIKLI': 'С принтом', 'DAMLA': 'С принтом', 'HAYVANLI': 'С принтом', 'KAPLUMBAĞA': 'С принтом', 'RAKUN': 'С принтом', 'BURCU': 'С принтом', 'YIRTMAÇLI': 'С разрезом', 'LASTIKLI': 'С Резинкой', 'KEMERLI': 'с ремнём', 'KEMERLİ': 'с ремнём', 'KEMER': 'с ремнём', 'KUŞAKLI': 'с ремнём', 'KUSAKLI': 'с ремнём', 'GÖMLEKLİ': 'С рубашкой', 'GOMLEKLI': 'С рубашкой', 'GÖMLEKLI': 'С рубашкой', 'KOLLU': 'С рукавом', 'FILELI': 'с сеткой', 'FILE': 'с сеткой', 'ÇANTALI': 'С сумкой', 'CANTALI': 'С сумкой', 'KÜLOTLU': 'С Трусами', 'KILOTLU': 'С трусами', 'KİLOTLU': 'С трусами', 'TÜLLÜ': 'С тюлью', 'DESENLI': 'с узором', 'DESENLİ': 'с узором', 'DESEN': 'с узором', 'BATİK': 'с узором', 'KULAKLI': 'С ушами', 'TIŞÖRTLÜ': 'С футболкой', 'CICEKLI': 'С цветами', 'CICEK': 'С цветами', 'ÇİÇEKLİ': 'С цветами', 'PAPATYA': 'С цветами', 'PAPATYALI': 'С цветами', 'LILY': 'С цветами', 'PATLI': 'С цветами', 'GUL': 'С цветами', 'GÜLLÜ': 'С цветами', 'GULLU': 'С цветами', 'GÜL': 'С цветами', 'SAPKALI': 'С шапкой', 'ŞAPKALI': 'С шапкой', 'BERELI': 'С шапкой', 'ATKILI': 'С шарфом', 'ŞORTLU': 'С шортами', 'SORTLU': 'С шортами', 'SHORTLU': 'С шортами', 'ETEKLİ': 'С юбкой', 'ETKLI': 'С юбкой', 'ETEKLI': 'С юбкой', 'MENDİLİ': 'Салфетки', 'SİMLİ': 'Серебристый', '-GREY': '-серый', 'FİLE': 'Сетка', 'MAVI': 'Синий', 'KARIŞIK': 'Смешанный', 'KARISIK': 'Смешанный', 'UYKU': 'Спать', 'ÖNDEN': 'Спереди', 'ONDEN': 'Спереди', 'ÖZEL': 'Специальный', 'SIRT': 'Спина', 'SPOR': 'Спорт', 'SPORT': 'Спорт', 'STANDART': 'Стандартный', 'KAPİTONE': 'Стеганная', 'KAPITONE': 'Стеганная', 'STYLE': 'Стиль', 'YAN': 'сбоку', 'YANDAN': 'сбоку', 'YANLAR': 'сбоку', 'SÜPREM': 'Сюрприз', 'BEL': 'Талия', 'BELI': 'Талия', 'BELDEN': 'Талия', 'İNCE': 'Тонкий', 'NCI': 'Тонкий', 'INCE': 'Тонкий', 'ALIŞTIRMA': 'Тренировочный', 'TERMAL': 'Утепленный', 'FIGÜRLÜ': 'Фигура', 'FIGURLU': 'Фигура', 'SAKLAMA': 'Хранение', 'RENKLI': 'Цветные', 'RENKLİ': 'Цветные', 'PARÇALAR': 'Часть', 'SIYAH': 'Черный', 'BLACK': 'Черный', 'OKUL': 'Школа', 'PARCA': 'ШТ', 'Lİ': 'шт', 'LÜ': 'шт', 'LU': 'шт', 'LI': 'Шт', 'PARÇA': 'шт', 'PRÇ': 'шт', 'PARÇALI': 'шт', 'PACA': 'Штанина', 'EKO': 'Эко', 'ORGANİC': 'Эко', '-ECRU': '-КРЕМОВЫЙ', 'BABY': 'Малыш', 'AY': 'Малыш', 'AYLIK': 'Малыш', 'BEBE': 'Малыш', '"Ay': 'Малыш', 'BEBEK': 'Малыш', 'BORN': 'Малыш', 'YENİ': 'Малыш', 'DOĞAN': 'Малыш', 'YENİDOĞAN': 'Малыш', '(BABY': 'Малыш', 'AY)': 'Малыш', '0-3-6AY': 'Малыш', '3-6-9': 'Малыш', '3-6-9AY': 'Малыш', '03-12AY': 'Малыш', '06-12AY': 'Малыш', '06-18AY': 'Малыш', '6-18AY': 'Малыш', '06-24AY': 'Малыш', '09-24AY': 'Малыш', '9-12-18AY': 'Малыш', '9-12-18': 'Малыш', 'YAS': 'Ребенок', 'ÇOCUK': 'Ребенок', 'COCUK': 'Ребенок', 'YAŞ': 'Ребенок', 'yaş': 'Ребенок', 'Y': 'Ребенок', 'ÇOÇUK': 'Ребёнок', 'ÇOCUĞU': 'Ребёнок', '1-ÇOCUK': 'Ребёнок', '3-ÇOCUK': 'Ребёнок', '2-3-5-7': 'Ребёнок', '1-3Y': 'Ребёнок', '1-4Y': 'Ребёнок', '2-5Y': 'Ребёнок', '3-6Y': 'Ребёнок', '3-7Y': 'Ребёнок', '4-6Y': 'Ребёнок', '5-8Y': 'Ребёнок', '6-9Y': 'Ребёнок', '7-10Y': 'Ребёнок', '8-12Y': 'Ребёнок', '9-12Y': 'Ребёнок', '10-11-12': 'Ребёнок', '13-16Y': 'Ребёнок', '10 LI': '10 шт', '10 Lİ': '10 шт', '10 LU': '10 шт', '10 LÜ': '10 шт', '10 PARÇA': '10 шт', '10 PÇ': '10 шт', '10 PRÇ': '10 шт', '10LI': '10 шт', "10'LI": '10 шт', '10Lİ': '10 шт', "10'Lİ": '10 шт', '10LU': '10 шт', "10'LU": '10 шт', '10LÜ': '10 шт', "10'LÜ": '10 шт', '10PARÇA': '10 шт', "10'PARÇA": '10 шт', '10PÇ': '10 шт', "10'PÇ": '10 шт', '10PRÇ': '10 шт', "10'PRÇ": '10 шт', '11 LI': '11 шт', '11 Lİ': '11 шт', '11 LU': '11 шт', '11 LÜ': '11 шт', '11 PARÇA': '11 шт', '11 PÇ': '11 шт', '11 PRÇ': '11 шт', '11LI': '11 шт', "11'LI": '11 шт', '11Lİ': '11 шт', "11'Lİ": '11 шт', '11LU': '11 шт', "11'LU": '11 шт', '11LÜ': '11 шт', "11'LÜ": '11 шт', '11PARÇA': '11 шт', "11'PARÇA": '11 шт', '11PÇ': '11 шт', "11'PÇ": '11 шт', '11PRÇ': '11 шт', "11'PRÇ": '11 шт', '12 LI': '12 шт', '12 LU': '12 шт', '12 LÜ': '12 шт', '12 PARÇA': '12 шт', '12 PÇ': '12 шт', '12 PRÇ': '12 шт', '12LI': '12 шт', "12'LI": '12 шт', '12LU': '12 шт', "12'LU": '12 шт', '12LÜ': '12 шт', "12'LÜ": '12 шт', '12PARÇA': '12 шт', "12'PARÇA": '12 шт', '12PÇ': '12 шт', "12'PÇ": '12 шт', '12PRÇ': '12 шт', "12'PRÇ": '12 шт', "12'Lİ": '12 шт', '3 LI': '3 шт', '3 Lİ': '3 шт', '3 LU': '3 шт', '3 LÜ': '3 шт', '3 PARÇA': '3 шт', '3 PÇ': '3 шт', '3 PRÇ': '3 шт', '3LI': '3 шт', "3'LI": '3 шт', '3Lİ': '3 шт', "3'Lİ": '3 шт', '3LU': '3 шт', "3'LU": '3 шт', '3LÜ': '3 шт', "3'LÜ": '3 шт', '3PARÇA': '3 шт', "3'PARÇA": '3 шт', '3PÇ': '3 шт', "3'PÇ": '3 шт', '3PRÇ': '3 шт', "3'PRÇ": '3 шт', '4 LI': '4 шт', '4 Lİ': '4 шт', '4 LU': '4 шт', '4 LÜ': '4 шт', '4 PARÇA': '4 шт', '4 PÇ': '4 шт', '4 PRÇ': '4 шт', '4LI': '4 шт', "4'LI": '4 шт', '4Lİ': '4 шт', "4'Lİ": '4 шт', '4LU': '4 шт', "4'LU": '4 шт', '4LÜ': '4 шт', "4'LÜ": '4 шт', '4PARÇA': '4 шт', "4'PARÇA": '4 шт', '4PÇ': '4 шт', "4'PÇ": '4 шт', '4PRÇ': '4 шт', "4'PRÇ": '4 шт', '5 LI': '5 шт', '5 Lİ': '5 шт', '5 LU': '5 шт', '5 LÜ': '5 шт', '5 PARÇA': '5 шт', '5 PÇ': '5 шт', '5 PRÇ': '5 шт', '5LI': '5 шт', "5'LI": '5 шт', '5Lİ': '5 шт', "5'Lİ": '5 шт', '5LU': '5 шт', "5'LU": '5 шт', '5LÜ': '5 шт', "5'LÜ": '5 шт', '5PARÇA': '5 шт', "5'PARÇA": '5 шт', '5PÇ': '5 шт', "5'PÇ": '5 шт', '5PRÇ': '5 шт', "5'PRÇ": '5 шт', '6 LI': '6 шт', '6 LU': '6 шт', '6 LÜ': '6 шт', '6 PARÇA': '6 шт', '6 PÇ': '6 шт', '6 PRÇ': '6 шт', '6LI': '6 шт', "6'LI": '6 шт', '6LU': '6 шт', "6'LU": '6 шт', '6LÜ': '6 шт', "6'LÜ": '6 шт', '6PARÇA': '6 шт', "6'PARÇA": '6 шт', '6PÇ': '6 шт', "6'PÇ": '6 шт', '6PRÇ': '6 шт', "6'PRÇ": '6 шт', '7 LI': '7 шт', '7 LU': '7 шт', '7 LÜ': '7 шт', '7 PARÇA': '7 шт', '7 PÇ': '7 шт', '7 PRÇ': '7 шт', '7LI': '7 шт', "7'LI": '7 шт', '7LU': '7 шт', "7'LU": '7 шт', '7LÜ': '7 шт', "7'LÜ": '7 шт', '7PARÇA': '7 шт', "7'PARÇA": '7 шт', '7PÇ': '7 шт', "7'PÇ": '7 шт', '7PRÇ': '7 шт', "7'PRÇ": '7 шт', '8 LI': '8 шт', '8 LU': '8 шт', '8 LÜ': '8 шт', '8 PARÇA': '8 шт', '8 PÇ': '8 шт', '8 PRÇ': '8 шт', '8LI': '8 шт', "8'LI": '8 шт', '8LU': '8 шт', "8'LU": '8 шт', '8LÜ': '8 шт', "8'LÜ": '8 шт', '8PARÇA': '8 шт', "8'PARÇA": '8 шт', '8PÇ': '8 шт', "8'PÇ": '8 шт', '8PRÇ': '8 шт', "8'PRÇ": '8 шт', '9 LI': '9 шт', '9 LU': '9 шт', '9 LÜ': '9 шт', '9 PARÇA': '9 шт', '9 PÇ': '9 шт', '9 PRÇ': '9 шт', '9LI': '9 шт', "9'LI": '9 шт', '9LU': '9 шт', "9'LU": '9 шт', '9LÜ': '9 шт', "9'LÜ": '9 шт', '9PARÇA': '9 шт', "9'PARÇA": '9 шт', '9PÇ': '9 шт', "9'PÇ": '9 шт', '9PRÇ': '9 шт', "9'PRÇ": '9 шт', '16-18NO': '16-18 размер', 'U.KOL': 'Длинный рукав', 'Y.KOL': 'Длинный рукав', 'U.KOLLU': 'Длинный рукав', 'UZUN KOL': 'Длинный рукав', 'K.KOL': 'Короткий рукав', 'K.KOLLU': 'Короткий рукав', 'KISA KOL': 'Короткий рукав', '3İP': 'Утепленный', '3IP': 'Утепленный', '3 İP': 'Утепленный', '3 IP': 'Утепленный', "'LU": 'шт', 'CM': 'см'}

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
checker = " "
err = " "
K2_old = " "

list_of_all_category = []
category_detail = []
all_category_urls_little = []
all_category_urls_main = []
product_links = []

def get_main_categories(driver: webdriver) -> list[BeautifulSoup]:
    r = driver.get("https://www.maxbabi.com")
    # get pack of all categories in every section(in ERKEK, in KIZ...)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "dropdown.pos-s.col-xs-w100.col-xs-left")))
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    main_categories = soup.find_all("li", class_="dropdown pos-s col-xs-w100 col-xs-left")
    for main_category in main_categories:
        list_of_all_category.append(main_category)
    return list_of_all_category

def get_categories(list_of_all_category: list, driver: webdriver) -> None:
    #get name of main category(ERKEK, KIZ...), link and name of every little category
    for main_category in list_of_all_category:
        all_category_urls_little = []
        # main_category_title
        K1 = main_category.find("span", class_="ceviri_def").text
        all_category_urls_little.append(K1)
        categories = main_category.find_all("a", class_="col-md-4 col-sm-6 col-xs-12 p10 black op8 soft colored-hover colored-hover-text4 fs14")
        for i in categories:
            category_url = i.get('href')
            print(category_url)
            all_category_urls_little.append(category_url)
        all_category_urls_main.append(all_category_urls_little)
    for i in all_category_urls_main:
        K1 = i[0]
        # print("title:", K1)
        #go to page with products in every category
        for j in range(1, len(i)):
            driver.get(i[j])
            a = True
            while a == True:
                try:
                    soup = BeautifulSoup(driver.page_source, features="html.parser")
                    get_product_links(soup, K1, driver)
                    next_page = soup.find_all("a", class_="arial-bold colored-bg soft colored-hover2 t-center lh30 in-block white fs9")[-1].get('href')
                    print("next page:", next_page)
                    driver.get(next_page)
                except Exception as e:
                    print(e)
                    a = False


def get_product_links(soup: BeautifulSoup, K1: str, driver: webdriver) -> None:
    product_links = []
    K1 = K1
    #get item link
    product_links_on_page = soup.find_all("a", class_="visual w100 left inside-zoom")
    for url in product_links_on_page:
        product_link = url.get('href')
        product_links.append(product_link)
        print(product_link)
    product_links_checker(product_links, K1, driver)


def product_links_checker(product_links: list[str], K1: str, driver: webdriver) -> None:
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
            r = driver.get(product_link)
            soup = BeautifulSoup(driver.page_source, features="html.parser")
            product_url = driver.current_url
            count_field = driver.find_element(By.XPATH,
                                              '/html/body/section[1]/div/div/div[2]/section/form/div[2]/div[2]/input')
            count_field.send_keys('1000')
            count_field.send_keys(Keys.ENTER)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sweet-alert.showSweetAlert.visible")))
            count_text = driver.find_element(By.CLASS_NAME, 'sweet-alert.showSweetAlert.visible').text
            if 'Stok nedeniyle ekleme yapılamıyor' in count_text:
                checker = 0
            else:
                checker = count_text.split('yerine ')[1].split(' adet')[0]
            print(checker)
            K2 = soup.find("a", class_="colored2").text
            K2_old = K2
            K1 = "XBA " + K1 + " - " + K2
            name = soup.find("div", class_="w100 left dinpro-bold fs28 pt15 pb15 urunadi col-xs-pt5 col-xs-pb5 col-xs-fs14").text.strip()
            # print(name)
            price = soup.find("span", class_="fiyattr").text.strip().replace("₺","")
            # print(price)
            paket_adedi = soup.find_all("span", class_="titillium-bold block")[3].text.strip().split("\n")[0].strip()
            # print(paket_adedi)
            urun_kodu = "XBA-" + soup.find("span", class_="titillium-bold block").text.strip().replace("#", "")
            # print(urun_kodu)
            brand = soup.find("a", class_="black op6 colored-hover-text").text.strip()
            aciklama = soup.find("span", class_="titillium-bold aciklama").text.replace(' ', '').replace('\n', '').strip()
            try:
                size = soup.find_all("span", class_="titillium-bold block")[2].text.strip().split("\n")[0].strip()
            except Exception as e:
                size = ""
            # print(yas_grubu)
            imgs_list = []
            for img in soup.find_all("img", class_="img-responsive b-white cur-p"):
                imgs_list.append(img.get("src"))
            imgs = "; ".join(imgs_list)
            imgs_row=[img_1,img_2,img_3,img_4,img_5,img_6,img_7,img_8,img_9,img_10,img_11,img_12,img_13,img_14,img_15]
            for x in range(0, 15):
                try:
                    imgs_row[x] = imgs_list[x]
                except Exception as e:
                    imgs_row[x] = " "
            renkle_list = []
            renkle = soup.find("select", class_="form-control dropup drRenkSecenek bb1 bl1 br1 bt1 bc1 bsn on b-ra5").text.strip().lower().split("\n")
            for renk in renkle:
                renkle_list.append(renk)
            renkle = "; ".join(renkle_list)
            # print(renkle)
            renkle_row = [renk_1, renk_2, renk_3, renk_4, renk_5, renk_6, renk_7, renk_8, renk_9, renk_10, renk_11, renk_12, renk_13, renk_14, renk_15]
            for x in range(0, 15):
                try:
                    renkle_row[x] = renkle_list[x].upper()
                except Exception as e:
                    renkle_row[x] = " "
            try:
                sezon = soup.find_all("span", class_="titillium-bold block")[4].text.strip()
            except:
                sezon = ""
            # print(sezon)
            row = f"{product_url}#{K1}#{K2}#{name}#{price}#{price2}#{aciklama}#{beden_seciniz}#{birim}#{brand}" \
                  f"#{code}#{count}#{paket_adedi}#{paket_fiyati}#{paket_sayisi_seciniz}#{urun_aciklama}#{urun_detaylari}#{urun_kodu}" \
                  f"#{yas_grubu}#{size}#{imgs}#{renkle}#{'#'.join(imgs_row)}#{'#'.join(renkle_row)}#{sezon}#{checker}"
            print(row)
            if int(checker) >= request_count:
                if not 'XBA-4577MS' in row:
                    with open(f"maxbabi {date}.csv", mode="a", encoding='utf-8') as w_file:
                        file_writer = csv.writer(w_file, delimiter="^", lineterminator="\r")
                        write_row = row.split("#")
                        if len(write_row) > 30:
                            if write_row[0] != '' and write_row[1] != '' and write_row[2] != '' and write_row[3] != '' and write_row[20] != ''and write_row[20] != ' ':
                                file_writer.writerow(write_row)
                            else:
                                pass
                        w_file.close()
            else:
                print('Мало товара')
        except Exception as e:
            print(product_link)

def cart_cleaner(driver: webdriver) -> None:
    driver.get('https://www.maxbabi.com/site/sepetim')
    delete_urls = []
    links_parts = driver.find_elements(By.CLASS_NAME, 'col-md-2.col-sm-2.col-xs-12.center-h.col-sm-pos-a.col-sm-lr0.col-sm-lt17')
    buttons = []
    for part in links_parts:
        button = part.find_elements(By.CLASS_NAME, 'left')[-1]
        buttons.append(button)
    for link in buttons:
        delete_urls.append(link.find_element(By.TAG_NAME, 'a').get_attribute('href'))
    print(delete_urls)
    for i in delete_urls:
        driver.get(i)

def main() -> None:
    with open(f"maxbabi {date}.csv", mode="w", encoding='utf-8') as w_file:
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
    options.add_argument("--headless")
    prefs = {'profile.default_content_setting_values': {'images': 2}}
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_experimental_option('prefs', prefs)
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    # options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1024,720")

    driver = webdriver.Chrome(chrome_options=options)

    driver.get('https://www.maxbabi.com/uye/giris')
    login = driver.find_element(By.ID, 'e_email')
    login.clear()
    login.send_keys('rafik1999@inbox.ru')
    time.sleep(3)
    password = driver.find_element(By.ID, 'e_sifre')
    password.clear()
    password.send_keys('300878raf')
    driver.find_element(By.CLASS_NAME,
                        'btn.btn-black.btn-block.btn-lg.b-ra0.colored-bg.white.arial-bold.fs14.p15').click()
    time.sleep(1)
    cart_cleaner(driver)
    get_main_categories(driver)
    get_categories(list_of_all_category, driver)


    read_file = pd.read_csv(f"maxbabi {date}.csv", sep='^', engine='python')
    read_file.to_excel(f"maxbabi {date}.xlsx", index=False, header=True)


def send_results() -> None:
    subject = "Обновление ассортимента"
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