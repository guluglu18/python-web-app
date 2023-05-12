import requests
from bs4 import BeautifulSoup


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

    

    #print(tip)

    
    print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------")






