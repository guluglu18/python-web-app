from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup
from sqlalchemy import text



app = Flask(__name__)
#Konekcija na bazu podataka
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/nekretnine' 
db = SQLAlchemy(app)
with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print('Uspešno povezivanje na bazu podataka')
        except Exception as e:
            print('Greška prilikom povezivanja na bazu podataka:', str(e))



#Definisanje modela za Kucu sa atributima
class Kuca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tip_nekretnine = db.Column(db.String)
    tip_ponude = db.Column(db.String)
    deo_grada = db.Column(db.String)
    grad = db.Column(db.String)
    drzava = db.Column(db.String)
    kvadratura = db.Column(db.String)
    uknjizenost = db.Column(db.String)
    spratnost = db.Column(db.String)
    broj_soba = db.Column(db.Integer)
    broj_kupatila = db.Column(db.Integer)

    #Konstrukotr
    def __init__(self, tip_nekretnine, tip_ponude, deo_grada, grad, drzava, kvadratura, uknjizenost, spratnost, broj_soba, broj_kupatila):
        self.tip_nekretnine = tip_nekretnine
        self.tip_ponude = tip_ponude
        self.deo_grada = deo_grada
        self.grad = grad
        self.drzava = drzava
        self.kvadratura = kvadratura
        self.uknjizenost = uknjizenost
        self.spratnost = spratnost
        self.broj_soba = broj_soba
        self.broj_kupatila = broj_kupatila


#definisanje modela Stan sa atributima
class Stan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tip_nekretnine = db.Column(db.String)
    tip_ponude = db.Column(db.String)
    deo_grada = db.Column(db.String)
    grad = db.Column(db.String)
    drzava = db.Column(db.String)
    kvadratura = db.Column(db.String)
    uknjizenost = db.Column(db.String)
    spratnost = db.Column(db.String)
    broj_soba = db.Column(db.Integer)
    broj_kupatila = db.Column(db.Integer)
    
    #Konstruktor
    def __init__(self, tip_nekretnine, tip_ponude, deo_grada, grad, drzava, kvadratura, uknjizenost, spratnost, broj_soba, broj_kupatila):
        self.tip_nekretnine = tip_nekretnine
        self.tip_ponude = tip_ponude
        self.deo_grada = deo_grada
        self.grad = grad
        self.drzava = drzava
        self.kvadratura = kvadratura
        self.uknjizenost = uknjizenost
        self.spratnost = spratnost
        self.broj_soba = broj_soba
        self.broj_kupatila = broj_kupatila



def crawl_nekretnine():
    url = 'https://www.nekretnine.rs/stambeni-objekti/lista/po-stranici/10/'
    response = requests.get(url)
    podatak = {}
    if response.status_code == 200:
        #Parsiranje
        soup = BeautifulSoup(response.content, 'html.parser')
        div = soup.find('div', class_ = 'advert-list')
        lista_nekretnine = div.find_all('div', class_ = 'row offer')
        
        #deoGrada, grad, drzava, tip_nekretnine, kvadratura, tip_ponude, spratnost, uknjizenost, brSoba, brKupatila
        for nekretnina in lista_nekretnine:
            #podaci o lokaciji 
            locations = nekretnina.find('p',  class_='offer-location text-truncate')
            locations = locations.text.strip().split(',')
            for location in locations:
                if len(locations) == 3:
                    podatak['deo_grada'] = locations[0]
                    podatak['grad'] = locations[1]
                    podatak['drzava'] = locations[2]
                else:
                    podatak['deo_grada'] = locations[0]
                    podatak['drzava'] = locations[1]

            #podaci o tipu nekretnine
            tip = nekretnina.find('div', class_='mt-1 mt-lg-2 mb-lg-0 d-md-block offer-meta-info offer-adress').text.strip().split('|')
            kuca = 'kuća'
            stan = 'stan'
            if kuca in tip[2]:
                podatak['tip_nekretnine'] = 'kuca'
            elif stan in tip[2]:
                podatak['tip_nekretnine'] = 'stan'
            else:
                podatak['tip_nekretnine'] = None

            #podaci o tipu ponude
            if (tip[1] == 'Izdavanje'):
                podatak['tip_ponude'] = tip[1].strip()
            else:
                podatak['tip_ponude'] = tip[1].strip()
            
            #podaci o kvadratri
            kv = nekretnina.find('p', class_ = 'offer-price offer-price--invert').text.split(' ')
            podatak['kvadratura'] = kv[0].strip()

            #pribavaljanje podataka koji se nalaze unutar linka: spratnost, uknjizenost, podaci
            for link in lista_nekretnine:
                link = nekretnina.find('a')['href']
            newUrl = 'https://www.nekretnine.rs'+link
            response = requests.get(newUrl)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                detalji = soup.find('section', class_='tabSectionContent')
                div = detalji.find('div', class_='property__amenities')
                ul = div.find('ul')
                li_elements = ul.find_all('li')

                for li in li_elements: 
                    if 'Spratnost' in li.text:
                        podatak['spratnost'] = li.text.strip().split(':')[1].strip()
                        #print('Spratnost: ' + podatak['spratnost'])
                    else:
                        podatak['spratnost'] = None
                    if 'Uknjiženo' in li.text:
                        podatak['uknjizenost'] = li.text.strip().split(':')[1].strip()
                        #print('Uknjizeno: ' + podatak['uknjizenost'])
                    else:
                        podatak['uknjizenost'] = None
                    if 'Ukupan broj soba' in li.text:
                        podatak['broj_soba'] = li.text.strip().split(':')[1].strip()
                        #print('Br soba: ' + podatak['broj_soba'])
                    else: 
                        #print('Br soba nije pronadjen')
                        podatak['broj_soba'] = None
                    if 'Broj kupatila' in li.text:
                        podatak['broj_kupatila'] = li.text.strip().split(':')[1].strip()
                        #print('Br kupatila:' + podatak['broj_kupatila'])
                    else: 
                        #print('Br soba nije pronadjen')
                        podatak['broj_kupatila'] = None
            else:
                print('Greška prilikom pristupa web stranici')
            print("------------------------------------------------------")
            for kljuc, vrednost in podatak.items():
                print(f'{kljuc}: {vrednost}')
            with app.app_context():
                if podatak['tip_nekretnine'] == 'kuća':
                    nova_kuca = Kuca(
                        tip_nekretnine=podatak['tip_nekretnine'],
                        tip_ponude=podatak['tip_ponude'],
                        deo_grada=podatak['deo_grada'],
                        grad=podatak['grad'],
                        drzava=podatak['drzava'],
                        kvadratura=podatak['kvadratura'],
                        uknjizenost=podatak['uknjizenost'],
                        spratnost=podatak['spratnost'],
                        broj_soba=podatak['broj_soba'],
                        broj_kupatila=podatak['broj_kupatila']
                    )
                    try:
                        db.session.add(nova_kuca)
                        db.session.commit()
                        print("Zapis je uspešno dodat u bazu podataka.")
                    except Exception as e:
                        print("Došlo je do greške pri dodavanju zapisa u db:", str(e))
                if podatak['tip_nekretnine'] == 'stan':
                    novi_stan = Stan(
                        tip_nekretnine=podatak['tip_nekretnine'],
                        tip_ponude=podatak['tip_ponude'],
                        deo_grada=podatak['deo_grada'],
                        grad=podatak['grad'],
                        drzava=podatak['drzava'],
                        kvadratura=podatak['kvadratura'],
                        uknjizenost=podatak['uknjizenost'],
                        spratnost=podatak['spratnost'],
                        broj_soba=podatak['broj_soba'],
                        broj_kupatila=podatak['broj_kupatila']
                    )
                    try:
                        db.session.add(novi_stan)
                        db.session.commit()
                        print("Zapis je uspešno dodat u bazu podataka.")
                    except Exception as e:
                        print("Došlo je do greške pri dodavanju zapisa u db:", str(e))
    else:
        print('Greška prilikom pristupa web stranici')
    


@app.route('/')
def index():
    return 'Dobrodošli na početnu stranicu'


@app.route('/nekretnine/<int:id>', methods=['GET'])
def get_nekretnina(id):
    # Provjeri postoji li nekretnina s traženim ID-om u bazi podataka
    nekretnina = Kuca.query.get(id) or Stan.query.get(id)
    
    if nekretnina is None:
        return jsonify({'error': 'Nekretnina nije pronađena'}), 404
    
    # Vrati nekretninu kao JSON odgovor
    return jsonify({
        'id': nekretnina.id,
        'tip_nekretnine': nekretnina.tip_nekretnine,
        'tip_ponude': nekretnina.tip_ponude,
        'deo_grada': nekretnina.deo_grada,
        'grad': nekretnina.grad,
        'drzava': nekretnina.drzava,
        'kvadratura': nekretnina.kvadratura,
        'uknjizenost': nekretnina.uknjizenost,
        'spratnost': nekretnina.spratnost,
        'broj_soba': nekretnina.broj_soba,
        'broj_kupatila': nekretnina.broj_kupatila
    })

@app.route('/nekretnine', methods=['GET'])
def pretrazi_nekretnine():
    tip = request.args.get('tip')
    min_kvadratura = request.args.get('min_kvadratura', type=float)
    max_kvadratura = request.args.get('max_kvadratura', type=float)
    parking = request.args.get('parking', type=bool)

    # Početni query za pretragu
    query = Stan.query

    # Filtriranje prema tipu nekretnine
    if tip:
        query = query.filter_by(tip_nekretnine=tip)

    # Filtriranje prema minimalnoj kvadraturi
    if min_kvadratura is not None:
        query = query.filter(Stan.kvadratura >= min_kvadratura)

    # Filtriranje prema maksimalnoj kvadraturi
    if max_kvadratura is not None:
        query = query.filter(Stan.kvadratura <= max_kvadratura)
        
    # Izvršavanje upita i dohvatanje rezultata
    rezultati = query.all()

    # Pretvaranje rezultata u JSON format
    rezultati_json = []
    for nekretnina in rezultati:
        rezultati_json.append({
            'id': nekretnina.id,
            'tip_nekretnine': nekretnina.tip_nekretnine,
            'tip_ponude': nekretnina.tip_ponude,
            'deo_grada': nekretnina.deo_grada,
            'grad': nekretnina.grad,
            'drzava': nekretnina.drzava,
            'kvadratura': nekretnina.kvadratura,
            'uknjizenost': nekretnina.uknjizenost,
            'spratnost': nekretnina.spratnost,
            'broj_soba': nekretnina.broj_soba,
            'broj_kupatila': nekretnina.broj_kupatila
        })

    return jsonify(rezultati_json)

if __name__ == '__main__':
    # Prikupljanje podataka sa web stranice pre pokretanja aplikacije
    crawl_nekretnine()
    app.run()