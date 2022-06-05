
from random import random
from urllib import response
from bs4 import BeautifulSoup
import requests
import re
import os
import json
from time import sleep

from mechanize import Browser
br = Browser()

# Ignore robots.txt
br.set_handle_robots( False )

image_counter = 1

links = [
    'https://www.eleconomista.es/ecomotor/clasificacion/cabrio',
    'https://www.eleconomista.es/ecomotor/clasificacion/berlina',
    'https://www.eleconomista.es/ecomotor/clasificacion/coupe',
    'https://www.eleconomista.es/ecomotor/clasificacion/berlina',
    'https://www.eleconomista.es/ecomotor/clasificacion/4x4',
    'https://www.eleconomista.es/ecomotor/clasificacion/familia',
    'https://www.eleconomista.es/ecomotor/clasificacion/monovolumen'
    ]

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

# links = ['https://www.eleconomista.es/ecomotor/clasificacion/cabrio']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
payload = {
    'query': 'test'
}

base_url = 'https://www.eleconomista.es/'

final_json = []

def dump_json():
    with open('data.json', 'w') as outfile:
        json.dump(final_json, outfile)

def process_car(link, brand):

    # sleep(10)
    
    global image_counter

    car_entry = {}

    response3 = br.open(base_url + link).read()
    soup = BeautifulSoup(response3, 'html.parser')
    try:
        car_entry['brand'] = brand
        car_entry['model'] = soup.find('h1').text
    
        images = soup.find_all('ul', {"class": "slides"})
    
        equipamiento = soup.find('ul', {"id": "equipamiento"})
        prestaciones = soup.find('ul', {"id": "prestaciones"})
    
        data_equipamiento = equipamiento.find_all('table', {"class": "flat-table flat-table-1"})
        data_prestaciones = prestaciones.find_all('table', {"class": "flat-table flat-table-1"})
    
        image_data = []
    
        for i in images:
            imgs = i.find_all('img')
            for i in imgs:
                img_url = i.get('src')
                if img_url[:2] == '//':
                    img_url = 'https:' + img_url
                os.makedirs(f'images/{brand}', exist_ok=True)
                try:
                    br.retrieve(img_url, f'images/{brand}/{image_counter}.jpg')
                    image_data.append(f'images/{brand}/{image_counter}.jpg')
                    image_counter += 1
                except Exception as e: 
                    print(str(e))
    
        car_entry['images'] = image_data

        for i in data_equipamiento+data_prestaciones:
            # print(i)
            header = i.find('h2').text
            car_entry[header] = {}

            table_data = i.find_all('tr')
            for j in table_data:
                k = j.find_all('th')
                k += j.find_all('td')
                if k[0] == '':
                    car_entry[header][k[1].text] = k[2].text
                else:
                    car_entry[header][k[0].text] = k[1].text

        final_json.append(car_entry)
    except:
        pass

def process_model(link, brand):
    response2 = br.open(link).read()
    soup = BeautifulSoup(response2, 'html.parser')
    div_versions = soup.find('div', {"class": "ft-versiones"})
    versions = [ i.get('href') for i in div_versions.find_all('a', {"itemprop": "url"}) ]
    
    for i in versions:
        if i[0] != '#':
            print(i)
            image_count = process_car(i, brand)
            break

for link in links:
    response = br.open(link).read()
    # response = requests.get(link, data=payload, headers=headers, verify=False)
    soup = BeautifulSoup(response, 'html.parser')

    model = soup.find('h1', {"class": "tit-modelo"})

    cars_list = soup.find('div', {"class": "cont-coche ficha-li"})
    brands = cars_list.find_all('h3')
    clean_brands = []

    for i in brands:
        clean_brands.append(clean_html(str(i)))

    lists = cars_list.find_all('div', {"class": "li-versiones"})
    
    for idx,cars in enumerate(lists):
        for car_link in cars.find_all('a'):
            process_model(car_link.get('href'), clean_brands[idx])

    dump_json()