import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import mysql.connector
from sqlalchemy.exc import OperationalError
import re

#konekcija sa bazom podataka
db_url = 'mysql+mysqlconnector://root:root@localhost/nekretnine'
engine = create_engine(db_url)

try:
    engine = create_engine(db_url)
    connection = engine.connect()
    print("Uspješno ste se povezali sa bazom podataka.")
    connection.close()
except OperationalError as e:
    print("Došlo je do greške prilikom povezivanja sa bazom podataka:", str(e))




#Prikupljanje podataka sa web sajta
html_text = requests.get('https://www.nekretnine.rs/stambeni-objekti/lista/po-stranici/10/')
content = html_text.content


soup = BeautifulSoup(content, 'html.parser')
div = soup.find('div', class_ = 'advert-list')
li = div.find_all('div', class_ = 'row offer')

for data in li:
    #podaci o lokaciji
    locations = data.find('p',  class_='offer-location text-truncate')
    locations = locations.text.strip().split(',')
    for location in locations:
        partOfCity = locations[0]
        city = locations[1]
        country = locations[2]
    #podaci o tipu nekretnine
    tip = data.find('div', class_='mt-1 mt-lg-2 mb-lg-0 d-md-block offer-meta-info offer-adress').text.strip().split('|')
    tip_p = tip[1]
    tip_n = tip[2]
    kuca = 'kuća'
    stan = 'stan'
    if kuca in tip_n:
        tip_nekretnine = kuca
        #insert into
        print(tip_nekretnine)
    elif stan in tip_n:
        tip_nekretnine = stan
        #insert into
        print(tip_nekretnine)
    else:
        print('Tip nije pronadjen')
    print("------------------------------------------------------------------")
    kv = data.find('p', class_ = 'offer-price offer-price--invert').text
    kvadratura = re.findall(r'\d+', kv)[0]
    print(kvadratura)
    print("------------------------------------------------------------------")

    

    #print(tip)

    
    






