from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/nekretnine'  # Zamijenite s odgovarajućim podacima
db = SQLAlchemy(app)

# Definisanje modela za nekretninu
class Nekretnina(db.Model):
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

# Funkcija za prikupljanje podataka sa web stranice
def crawl_nekretnine():
    url = 'https://www.nekretnine.rs/'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        #Prikupljanje podataka sa web sajta
        html_text = requests.get('https://www.nekretnine.rs/stambeni-objekti/lista/po-stranici/10/')
        content = html_text.content

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


    else:
        print('Greška prilikom pristupa web stranici')

@app.route('/')
def index():
    return 'Dobrodošli na početnu stranicu'


# API za dohvatanje nekretnine po id-ju
@app.route('/nekretnine/<int:nekretnina_id>', methods=['GET'])
def get_nekretnina(nekretnina_id):
    nekretnina = Nekretnina.query.get(nekretnina_id)
    if nekretnina:
        return jsonify(nekretnina.__dict__), 200
    else:
        return jsonify({'message': 'Nekretnina nije pronađena'}), 404

# API za pretraživanje nekretnina
@app.route('/nekretnine', methods=['GET'])
def pretrazi_nekretnine():
    tip = request.args.get('tip')
    min_kvadratura = request.args.get('min_kvadratura')
    max_kvadratura = request.args.get('max_kvadratura')
    parking = request.args.get('parking')

    query = Nekretnina.query

    if tip:
        query = query.filter_by(tip_nekretnine=tip)
    if min_kvadratura:
        query = query.filter(Nekretnina.kvadratura >= min_kvadratura)
    if max_kvadratura:
        query = query.filter(Nekretnina.kvadratura <= max_kvadratura)
    if parking:
        query = query.filter_by(parking=parking)

    nekretnine = query.all()
    rezultat = [nekretnina.__dict__ for nekretnina in nekretnine]

    return jsonify(rezultat), 200

# API za kreiranje nove nekretnine
@app.route('/nekretnine', methods=['POST'])
def kreiraj_nekretninu():
    data = request.get_json()
    nekretnina = Nekretnina(**data)
    db.session.add(nekretnina)
    db.session.commit()

    return jsonify({'message': 'Nekretnina je uspješno kreirana'}), 201

# API za promjenu podataka nekretnine
@app.route('/nekretnine/<int:nekretnina_id>', methods=['PUT'])
def promijeni_nekretninu(nekretnina_id):
    nekretnina = Nekretnina.query.get(nekretnina_id)
    if nekretnina:
        data = request.get_json()
        nekretnina.tip_nekretnine = data.get('tip_nekretnine', nekretnina.tip_nekretnine)
        nekretnina.tip_ponude = data.get('tip_ponude', nekretnina.tip_ponude)
        nekretnina.lokacija = data.get('lokacija', nekretnina.lokacija)
        # Dodajte ostale promjene podataka po želji

        db.session.commit()
        return jsonify({'message': 'Podaci nekretnine su uspješno promijenjeni'}), 200
    else:
        return jsonify({'message': 'Nekretnina nije pronađena'}), 404

if __name__ == '__main__':
    # Prikupljanje podataka sa web stranice prije pokretanja aplikacije
    crawl_nekretnine()
    app.run()

