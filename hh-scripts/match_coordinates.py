from bs4 import BeautifulSoup
import urllib.request
import requests
import re
import math
import numpy
import pandas as pd 

import json
import csv
from itertools import chain
from typing import List
from multiprocessing.dummy import Pool as ThreadPool 



def read_df(city_abbr):
    data = pd.read_csv(f'../hh-data/tables/{city_abbr}/fulltime/url-adress-salary.csv')
    return data


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
        

def get_lat_lon(adress):
    api_key = '04bce1f4-b257-45ac-acf5-673a9e894fc1'
    api_url = f'https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&format=json&geocode='
    r = requests.get(api_url+adress)
    d = json.loads(r.text)
    if d['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'] != 0:
        longitude, latitude = d['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
        return (latitude, longitude)
    return tuple()


def f(row):
    try:
        adress = row['adress'].replace(' ', '+')
        coordinates = get_lat_lon(adress)
        if coordinates:
            return ([row['url'], row['adress'], ', '.join([str(c) for c in coordinates]), row['salary']])
    except urllib.error.HTTPError:
        print(url)
    except IndexError:
        pass


def save_rows(city_abbr):

    rows = [row for index, row in read_df(city_abbr).iterrows()]
    row_chunks = chunks(rows, 100)


    for chunk in row_chunks:

        pool = ThreadPool(8) 

        results = pool.map(f, chunk)

        pool.close() 
        pool.join()

        with open(f"../hh-data/tables/{city_abbr}/fulltime/rows_with_lat_lon.txt", "a") as file:
            file.write('\n'.join(['; '.join([str(el) for el in row]) for row in results]) + '\n')
    
    with open(f"../hh-data/tables/{city_abbr}/fulltime/rows_with_lat_lon.txt") as file:
        rows = [line.split('; ') for line in file.read().replace("https", "\nhttps").split('\n')]
    rows = [row for row in rows if len(row) == 4]
    df = pd.DataFrame(rows)
    df.columns = ['url', 'adress', 'coordinates', 'salary']
    df.to_csv(f"../hh-data/tables/{city_abbr}/fulltime/url-adress-coord-salary.csv", index=False)


if __name__ == "__main__":

    save_rows("smr")
    save_rows("spb")
    save_rows("kzn")

    