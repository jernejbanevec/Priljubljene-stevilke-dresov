import requests
import re
import os
import csv

#=============================== UVOZ PODATKOV =======================================

# main page url (leta od 1950 - 2018)
# stevilke_dresov_url = 'https://www.basketball-reference.com/leagues/NBA_{}_numbers.html'.format(leto)

# directory
stevilke_dresov_directory = 'C:/Users\JernejPC\Documents\Jernej - Financna matematika\Programiranje 1\Priljubljene-stevilke-dresov\Podatki'

# ime CSV datoteke s podatki
podatki_stevilke_dresov_csv = "podatki.csv"


def download_url_to_string(url):
    ''' Funkcija, ki s pomočjo requests vrne string s podatki, če me slučajno ne zavrnejo.'''
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print("failed to connect to url " + url)
        return
    #ta del se nanaša ne del kode, kjer exception ni bil sprožen
    if r.status_code == requests.codes.ok:
        return r.text
    print("failed to download url " + url)
    return

def save_string_to_file(text, directory, filename):
    ''' Funkcija, ki text zapiše v ime z imenom "filename",
    to mapo tudi ustvari, če še ni bila ustvarjena.'''
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding = 'utf-8') as file_out:
        file_out.write(text)
    return None

# funkcija, ki uvozi podatke za vsa leta v dano mapo

def save_frontpages():
    '''Shrani "stevilke_dresov_url" to the file
    "stevilke_dresov_directory"/"podatki_stevilke_html"'''
    for leto in range(1950, 2019):
        url = 'https://www.basketball-reference.com/leagues/NBA_{}_numbers.html'.format(leto)
        ime_datoteke = 'stevilke_dresov_{}_html'.format(leto)
        text = download_url_to_string(url)
        save_string_to_file(text, stevilke_dresov_directory, ime_datoteke)
    return None


#=============================== PROCESIRANJE PODATKOV =======================================


def read_file_to_string(directory, filename):
    '''Vrne vsebino datoteke "directory"/"filename" kot obliko string.'''
    path = os.path.join(directory, filename)
    with open(path, 'r') as file_in:
        return file_in.read()
