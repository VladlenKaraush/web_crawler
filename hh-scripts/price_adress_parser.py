from bs4 import BeautifulSoup
import urllib.request
import requests
import re

import numpy
import pandas as pd 

import json
import csv
from itertools import chain
from typing import List
from multiprocessing.dummy import Pool as ThreadPool 



def basic_paerser_results_row(url: str) -> List[str]:
    results_response = urllib.request.urlopen(url)
    results_soup = BeautifulSoup(results_response)

    adress_spans = results_soup.findAll('span', {'data-qa': 'vacancy-view-raw-address'})
    salary_classes = results_soup.findAll('p', {'class': 'vacancy-salary'})
    
    return [url, adress_spans[0].contents[1] if adress_spans else '', salary_classes[0].contents[0] if salary_classes else '']


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def f(url):    
    try:
        row = basic_paerser_results_row(url)
        if not row[1]:
            no_adress_table.append(row)
        elif not row[2]:
            no_salary_table.append(row)
        else:
            completed_table.append(row)
    except urllib.error.HTTPError:
        print(url)
    except IndexError:
        pass


with open("../hh-data/urls/spb-fulltime-urls.txt") as file:
    urls = file.read().split('\n')

urls_chunks = chunks(urls[33999:], 100)
for chunk in urls_chunks:
    completed_table = []
    no_adress_table = []
    no_salary_table = []
    
    pool = ThreadPool(8) 

    results = pool.map(f, chunk)

    pool.close() 
    pool.join()
    
    with open("../hh-data/tables/spb/fulltime/completed.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in completed_table]))
        
    with open("../hh-data/tables/spb/fulltime/no-adress.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in no_adress_table]))



with open("../hh-data/urls/smr-fulltime-urls.txt") as file:
    urls = file.read().split('\n')

urls_chunks = chunks(urls, 100)
for chunk in urls_chunks:
    completed_table = []
    no_adress_table = []
    no_salary_table = []
    
    pool = ThreadPool(8) 

    results = pool.map(f, chunk)

    pool.close() 
    pool.join()
    
    with open("../hh-data/tables/smr/fulltime/completed.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in completed_table]))
        
    with open("../hh-data/tables/smr/fulltime/no-adress.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in no_adress_table]))



with open("../hh-data/urls/vdk-fulltime-urls.txt") as file:
    urls = file.read().split('\n')

urls_chunks = chunks(urls, 100)
for chunk in urls_chunks:
    completed_table = []
    no_adress_table = []
    no_salary_table = []
    
    pool = ThreadPool(8) 

    results = pool.map(f, chunk)

    pool.close() 
    pool.join()
    
    with open("../hh-data/tables/vdk/fulltime/completed.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in completed_table]))
        
    with open("../hh-data/tables/vdk/fulltime/no-adress.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in no_adress_table]))



with open("../hh-data/urls/kzn-fulltime-urls.txt") as file:
    urls = file.read().split('\n')

urls_chunks = chunks(urls, 100)
for chunk in urls_chunks:
    completed_table = []
    no_adress_table = []
    no_salary_table = []
    
    pool = ThreadPool(8) 

    results = pool.map(f, chunk)

    pool.close() 
    pool.join()
    
    with open("../hh-data/tables/kzn/fulltime/completed.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in completed_table]))
        
    with open("../hh-data/tables/kzn/fulltime/no-adress.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in no_adress_table]))


