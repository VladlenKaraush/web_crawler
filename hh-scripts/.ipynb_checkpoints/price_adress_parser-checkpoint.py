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


with open("./hh-data/urls/smr-urls.txt") as file:
    smr_urls = file.read().split('\n')

smr_urls_chunks = chunks(smr_urls, 100)
for chunk in smr_urls_chunks:
    completed_table = []
    no_adress_table = []
    no_salary_table = []
    
    pool = ThreadPool(8) 

    results = pool.map(f, chunk)

    pool.close() 
    pool.join()
    
    with open("./hh-data/tables/smr/completed.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in completed_table]) + '\n' )
        
    with open("./hh-data/tables/smr/no-adress.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in no_adress_table]) + '\n' * bool(len(no_adress_table)))
        
    with open("./hh-data/tables/smr/no-salary.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in no_salary_table]) + '\n' * bool(len(no_salary_table)))


with open("./hh-data/urls/kzn-urls.txt") as file:
    kzn_urls = file.read().split('\n')

kzn_urls_chunks = chunks(kzn_urls, 100)
for chunk in kzn_urls_chunks:
    completed_table = []
    no_adress_table = []
    no_salary_table = []
    
    pool = ThreadPool(8) 

    results = pool.map(f, chunk)

    pool.close() 
    pool.join()
    
    with open("./hh-data/tables/kzn/completed.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in completed_table]) + '\n' )
        
    with open("./hh-data/tables/kzn/no-adress.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in no_adress_table]) + '\n' * bool(len(no_adress_table)))
        
    with open("./hh-data/tables/kzn/no-salary.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in no_salary_table]) + '\n' * bool(len(no_salary_table)))


with open("./hh-data/urls/vdk-urls.txt") as file:
    vdk_urls = file.read().split('\n')

vdk_urls_chunks = chunks(vdk_urls, 100)
for chunk in vdk_urls_chunks:
    completed_table = []
    no_adress_table = []
    no_salary_table = []
    
    pool = ThreadPool(8) 

    results = pool.map(f, chunk)

    pool.close() 
    pool.join()
    
    with open("./hh-data/tables/vdk/completed.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in completed_table]) + '\n' )
        
    with open("./hh-data/tables/vdk/no-adress.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in no_adress_table]) + '\n' * bool(len(no_adress_table)))
        
    with open("./hh-data/tables/vdk/no-salary.csv", "a") as file:
        file.write('\n'.join(['; '.join(row) for row in no_salary_table]) + '\n' * bool(len(no_salary_table)))

    


