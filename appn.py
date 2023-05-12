from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
#Konekcija na bazu podataka
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/nekretnine'  # Zamijenite s odgovarajućim podacima
db = SQLAlchemy(app)

#Definisanje modela za Kucu
class Kuca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tip_nekretnine = db.Column(db.String)
    tip_ponude = db.Column(db.String)
    lokacija = db.Column(db.String)
    deo_grada = db.Column(db.String)
    kvadratura = db.Column(db.String)
    godina_izgradnje = db.Column(db.Integer)
    povrsina_zemljista = db.Column(db.String)
    uknjizenost = db.Column(db.String)
    tip_grejanja = db.Column(db.String)
    broj_soba = db.Column(db.Integer)
    broj_kupatila = db.Column(db.Integer)
    parking = db.Column(db.String)
    dodatne_informacije = db.Column(db.String)

    #Konstrukotr
    def __init__(self, tip_nekretnine, tip_ponude, lokacija, deo_grada, kvadratura, godina_izgradnje, povrsina_zemljista, uknjizenost, tip_grejanja, broj_soba, broj_kupatila, parking, dodatne_informacije):
        self.tip_nekretnine = tip_nekretnine
        self.tip_ponude = tip_ponude
        self.lokacija = lokacija
        self.deo_grada = deo_grada
        self.kvadratura = kvadratura
        self.godina_izgradnje = godina_izgradnje
        self.povrsina_zemljista = povrsina_zemljista
        self.uknjizenost = uknjizenost
        self.tip_grejanja = tip_grejanja
        self.broj_soba = broj_soba
        self.broj_kupatila = broj_kupatila
        self.parking = parking
        self.dodatne_informacije = dodatne_informacije

#definisanje modela Stan
class Stan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tip_nekretnine = db.Column(db.String)
    tip_ponude = db.Column(db.String)
    lokacija = db.Column(db.String)
    deo_grada = db.Column(db.String)
    kvadratura = db.Column(db.String)
    godina_izgradnje = db.Column(db.Integer)
    spratnost = db.Column(db.String)
    uknjizenost = db.Column(db.String)
    tip_grejanja = db.Column(db.String)
    broj_soba = db.Column(db.Integer)
    broj_kupatila = db.Column(db.Integer)
    parking = db.Column(db.String)
    dodatne_informacije = db.Column(db.String)

    #Konstruktor
    def __init__(self, tip_nekretnine, tip_ponude, lokacija, deo_grada, kvadratura, spratnost, povrsina_zemljista, uknjizenost, tip_grejanja, broj_soba, broj_kupatila, parking, dodatne_informacije):
        self.tip_nekretnine = tip_nekretnine
        self.tip_ponude = tip_ponude
        self.lokacija = lokacija
        self.deo_grada = deo_grada
        self.kvadratura = kvadratura
        self.spratnost = spratnost
        self.povrsina_zemljista = povrsina_zemljista
        self.uknjizenost = uknjizenost
        self.tip_grejanja = tip_grejanja
        self.broj_soba = broj_soba
        self.broj_kupatila = broj_kupatila
        self.parking = parking
        self.dodatne_informacije = dodatne_informacije



def crawl_nekretnine():
    url = 'https://www.nekretnine.rs/stambeni-objekti/lista/po-stranici/10/'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        div = soup.find('div', class_ = 'advert-list')
        li = div.find_all('div', class_ = 'row offer')
        #partOfCity, city, country, tip_nekretnine, kvadratura, tip_ponude, spratnost, uknjizenost, brSoba, brKupatila
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
                print('Tip nekretnine nije pronadjen')
            if (tip_p == 'Izdavanje'):
                tip_ponude = tip_p.strip()
            else:
                tip_ponude = tip_p.strip()
            print(tip_ponude)
            kv = data.find('p', class_ = 'offer-price offer-price--invert').text
            kvadratura = re.findall(r'\d+', kv)[0]
            print(kvadratura)

            for link in li:
                link = data.find('a')['href']
            newUrl = 'https://www.nekretnine.rs'+link
            response = requests.get(newUrl)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                detalji = soup.find('section', class_='tabSectionContent')
                div = detalji.find('div', class_='property__amenities')
                ul = div.find('ul')
                li_elements = ul.find_all('li')
                spratnost = None
                uknjizenost = None
                brSoba = None
                brKupatila = None
                for li in li_elements:
                    text = li.text.strip()  # Dobijanje teksta iz <li> elementa i uklanjanje praznina
                    if 'Spratnost' in text:
                        spratnost = text.split(' ')[-1]  # Izdvajanje poslednje reči kao vrednost spratnosti
                        if spratnost is not None:
                            print('Spratnost: ' + spratnost)
                        else:
                            print('Spratnost nije pronađena')
                    elif 'Uknjiženo' in text:
                        uknjizenost = text.split(' ')[-1]
                        if uknjizenost is not None:
                            print('Uknjizeno: ' + uknjizenost)
                        else:
                            print('Uknjizenost nije pronađena')
                    elif 'Ukupan broj soba' in text:
                        brSoba = text.split(' ')[-1]
                        if brSoba is not None:
                            print("Br soba: " + brSoba)
                        else:
                            print('Br soba nije pronadjen')
                    elif 'Broj kupatila' in text:
                        brKupatila = text.split(' ')[-1]
                        if brKupatila is not None:
                            print("Br kupatila: " + brKupatila)
                        else:
                            print('Br kupatila nije pronadjen')
            else:
                print('Greška prilikom pristupa web stranici')

            print(newUrl)
            print(link)
            print("------------------------------------------------------")
    else:
        print('Greška prilikom pristupa web stranici')

crawl_nekretnine()
