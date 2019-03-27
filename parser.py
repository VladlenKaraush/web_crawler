#!/usr/bin/env python
# coding: utf-8

# In[4]:


# url to first pages
# enter cian.ru and avito.ru urls of desired city and a name of the city
cian_url = "https://spb.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=2&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1"
# avito_url = "https://www.avito.ru/sankt-peterburg/kvartiry?s_trg=1"
avito_url = 'https://www.avito.ru/sankt-peterburg/kvartiry/prodam?f=549_5695-5696-5697-5698-5699-5700-5701-11018-11019-11020-11021&s_trg=4'
city = "Санкт-Петербург"

#example of samara urls
# avito_url = 'https://www.avito.ru/samara/kvartiry?s_trg=3'
# cian_url = 'https://samara.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=4966&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room9=1'
# city = 'Самара'

csv_dir = 'csv-data'
api_key = '800e1c1a-3d68-496e-88a9-009b98d7eb75'
api_url = 'https://geocode-maps.yandex.ru/1.x/?apikey=' + api_key + '&format=json&geocode=' + city + ',+'


# In[5]:


# execute this cell to load all neccessary functions

from bs4 import BeautifulSoup
import urllib.request
import requests
import re

#write collected data to .csv file as a pandas dataframe
import numpy
import pandas as pd 

#decode geotagging answer
import json
import csv

#avito
#extract price
def price_from_json(flat):
    price = flat.find("div", {"class": "popup-prices"})
    if price != None:
        price = price['data-prices']
    else:
        return -1
    price_ind = price.find('RUB":')
    price_cut = price[price_ind + 5:]
    price_in_rub = price_cut.split(",")[0]
    return int(price_in_rub)

#extract all relevant data from single page
def parse_page_avito(flats, data_flats):
    rent_count = 0
    print("flats on page: ", len(flats))
    for (index, flat) in enumerate(flats):

        print("Flat number", index)

        #price
        print("price:")
        price = price_from_json(flat)
        if(price < 300_000):
            rent_count += 1
            print("Rent found, skip. price = ", price)
            continue
        print(price)
        print()


        #rooms, area, floor level
        print("rooms:")
        description = flat.find("a", {"class": "item-description-title-link"})['title']
        try_rooms = description.split(",")[0][0]
        if try_rooms.isnumeric():
            rooms = int(try_rooms)
        else:
            rooms = 1
        print(rooms)
        print()

        print("area:")
        area = float(description.split(",")[1].split(" ")[1])
        print(area, "m^2")
        print()

        print(description)

        print("floor:")
        floor = description.split(",")[2].split(" ")[1].split("/")[0]
        print('floors total = ', description)
        floors_total = description.split(",")[2].split(" ")[1].split("/")[1]
        print("" + floor + ", total floors: " + floors_total)
        print()

        #subway, distance to subway, adress
        full_adress = flat.find("p", {"class": "address"}).getText()

        adress = ','.join(full_adress.split(",")[1:])
        print("adress:")
        print(adress)
        print()

        subway = full_adress.split(",")[0]
        for (ind,el) in enumerate(subway.split()):
            try:
                float(el)
                subway_station = ' '.join(subway.split()[:ind])
                distance = float(subway.split()[ind])
            except ValueError:
                pass

        print("subway:")
        print(subway_station)
        print()

        if distance < 99:
            distance *= 1000
        print("distance to subway:")
        print(distance, "meters")
        print()

        print("go to next page")
        data_flats.append((price, rooms, area, floor, floors_total, adress, subway_station, distance))
    
    print(rent_count)
    return data_flats


def parse_avito(avito_url):
    avito_real_estate = urllib.request.urlopen(avito_url).read()
    #parse avito with beautiful soup
    avito_soup = BeautifulSoup(avito_real_estate)
    # url_base = "https://www.avito.ru"
    flats = avito_soup.findAll("div", {"class":"item_table-description"})
    page_count = 0

    data_flats = parse_page_avito(flats, [])

    while True:
        try:
            page_count += 1
            print("Page: ", page_count)
            next_page = avito_soup.find("a", {"class":"pagination-page"}).get('href')
            flats = avito_soup.findAll("div", {"class":"item_table-description"})
            data_flats = parse_page_avito(flats, data_flats)

            if page_count > 100:
                print('page count > 100, break')
                break
        except Exception as error:
            print(error, ' error, break')
            break

    print("finish, page count = ", page_count)
    print("data len: ", len(data_flats))
    new_data_flats = []
    for flat in data_flats:
        new_flat = (flat[0],flat[1],flat[2],flat[3],flat[4],flat[5].replace('\xa0', '', 2),flat[6],flat[7])
        new_data_flats.append(new_flat)
    
    return new_data_flats

def write_to_csv(new_data_flats, file_name):
    
    a = numpy.asarray(new_data_flats)
    pd.DataFrame(a).to_csv(csv_dir + '/' + file_name, header=['price', 'rooms', 'area', 'floor', 'floors_total', 'adress',
                                           'subway_station', 'distance to subway'])

#cian
    
def next_page_cian(first_page, soup):
    next_p = soup.find("li", {"class": re.compile('^.*list-item--active.*')})
    if next_p and next_p.nextSibling:
        return next_p.nextSibling.a['href']
    else:
        return -1

def parse_cian_page(cian_soup, data_flats):
    counter = 0
    flats = cian_soup.findAll("div", {"class": "c6e8ba5398--info-container--YhZ2y"})
    print('flats = ',len(flats))
    for flat in flats:
        
        counter += 1
        # rooms, area, floor
        addr = flat.find("div", {"class": re.compile('^.*title.*')})
        if addr:
            try:
                rooms = int(addr.text[0])
                print('rooms = ', rooms)
            except Exception:
                rooms = 1
            try:
                area = float(addr.text.split(',')[1].split()[0])
            except Exception as error:
                print(error,', area error, area = ', addr.text.split(',')[1].split()[0])
                continue
            print('full addr = ', addr.text)
            print('area = ', area)
            floor = int(addr.text.split(',')[2].split(' ')[1].split('/')[0])
            print('floors = ', floor)
            try:
                floors_total = int(addr.text.split(',')[2].split(' ')[1].split('/')[1])
            except Exception as error:
                print('floors total error = ', error)
            print('floors total = ', floors_total)
            
            print(addr.text)

        subway = flat.find("div", {"class": re.compile('^.*underground-name.*')})
        if subway:
            subway = subway.text
            print(subway)
        else:
            subway = None

        remoteness = flat.find("div", {"class": re.compile('^.*remoteness.*')})
        if remoteness:
            print(remoteness.text)
            if remoteness.text.split('\xa0')[2] == 'пешком':
                remoteness = int(remoteness.text.split('\xa0')[0]) * 100
            else:
                remoteness = int(remoteness.text.split('\xa0')[0]) * 1000
            print('distance to subway = ',remoteness)
        else:
            remoteness = None
            
        adress = flat.findAll("a", {"class": re.compile('^.*address.*')})
        if adress:
            if(len(adress) > 5):
                adress = adress[4].text+ ', ' + adress[5].text
                print(adress)
            else:
                continue
                
        price = flat.find("div", {"class": re.compile('^.*price.*')}).find("div",{'class': re.compile('.*header.*')})
        if price:
            print(price.text)
            price_array = price.text.split(' ')[:len(price.text.split(' ')) - 1]
            price = 0
            for el in price_array:
                price *= 1000
                price += int(el)
            print('price = ', price)
            
        data_flats.append((price, rooms, area, floor, floors_total, adress, subway, remoteness))
        print()
    return data_flats

def parse_cian(cian_url):
    base_url = cian_url.split('cian.ru')[0] + 'cian.ru' 
    cian_real_estate = urllib.request.urlopen(cian_url).read()
    cian_soup = BeautifulSoup(cian_real_estate)
    counter = 0
    flats = []
    pages = 58
    while counter < pages:
        counter += 1
        flats = parse_cian_page(cian_soup, flats)
        cian_url = next_page_cian(cian_url, cian_soup)
        if cian_url == -1:
            break
        if base_url not in cian_url:
            cian_url = base_url + cian_url
        print("url = ", cian_url)
        cian_html = urllib.request.urlopen(cian_url).read()
        cian_soup = BeautifulSoup(cian_html)
        print("counter = ", counter)
    return flats
        
        
#add geotagging to existing csv file
def geotag(file_in, file_out):
    with open(file_in) as csv_file, open(file_out, 'w') as out:

        writer = csv.writer(out, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        csv_reader = csv.reader(csv_file, delimiter=',')
        for ind, row in enumerate(csv_reader):
            print('row ', ind)
            if ind == 0:
                writer.writerow((*row, 'longitude', 'latitude'))

            else:
                #TODO replace spaces with '+'
                print('requested address = ', row[6].replace(' ','+'))
                print('full url = ',api_url + row[6].replace(' ','+') )
                r = requests.get(api_url + row[6].replace(' ','+'))
                d = json.loads(r.text)
                if d['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'] != 0:
                    longitude, latitude = d['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
                    print('long = ', longitude, ', latitude = ', latitude)
                    writer.writerow((*row, longitude, latitude))
                    out.flush()
                else:
                    print("geoposition not found, row skipped")
                
#merge two data files
def merge(first, second, out):
    
    with open(first) as cian, open(second) as avito, open(out, 'w') as out:
        writer = csv.writer(out, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        cian_reader = csv.reader(cian, delimiter=',')
        avito_reader = csv.reader(avito, delimiter =',')

        for row in avito_reader:
            writer.writerow(row)

        for row in cian_reader:
            writer.writerow(row)


# In[ ]:


# необходимо сначала исполнить следующую ячейку, чтобы загрузить все функции
# работает долго

# avito to csv
print('start avito parsing, url = ', avito_url)
avito_flats = parse_avito(avito_url)
write_to_csv(avito_flats, 'spb_test_avito.csv')
print('finished avito parsing')

# cian to csv
print('start cian parsing, url = ', cian_url)
cian_flats = parse_cian(cian_url)
write_to_csv(cian_flats, 'spb_test_cian.csv')
print('finished cian parsing')

# merge
print('merging cian and avito data')
merge('spb_test_avito.csv', 'spb_test_cian.csv', 'spb_test_merged.csv')

# geotag
print('geotag all data')
geotag('spb_test_merged.csv', 'spb_test_geotagged.csv')

