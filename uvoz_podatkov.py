import requests
import re
import os
import csv

#=============================== UVOZ PODATKOV =======================================

# main page url (leta od 1950 - 2018)
# stevilke_dresov_url = 'https://www.basketball-reference.com/leagues/NBA_{}_numbers.html'.format(leto)

# directory
#DOMA:
stevilke_dresov_directory = 'C:/Users\JernejPC\Documents\Jernej - Financna matematika\Programiranje 1\Priljubljene-stevilke-dresov\Podatki'
igralci_directory = 'C:/Users\JernejPC\Documents\Jernej - Financna matematika\Programiranje 1\Priljubljene-stevilke-dresov\Podatki_igralci'
#NA FAKSU
#stevilke_dresov_directory = 'U:/Programiranje1\Priljubljene-stevilke-dresov\Podatki'

# ime CSV datoteke s podatki
podatki_stevilke_dresov_csv = "podatki.csv"
podatki_stevilke_dresov_csv2 = "podatki_igralci.csv"
# filepage
frontpage_filename = "stevilke_dresov_2018_html"
# ime zip datoteke
zip_ime = "zip_podatki_igralci_html"


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
    for leto in range(1965, 2019):
        url = 'https://www.basketball-reference.com/leagues/NBA_{}_numbers.html'.format(leto)
        ime_datoteke = 'stevilke_dresov_{}_html'.format(leto)
        text = download_url_to_string(url)
        save_string_to_file(text, stevilke_dresov_directory, ime_datoteke)
    return None


#=============================== PROCESIRANJE PODATKOV =======================================


def read_file_to_string(directory, filename):
    '''Vrne vsebino datoteke "directory"/"filename" kot obliko string.'''
    path = os.path.join(directory, filename)
    with open(path, 'r', encoding = 'utf-8') as file_in:
        return file_in.read()

def page_to_ads(page):
    '''Funkcija, ki razdeli kodo na bloke za vsako številko'''
    rx = re.compile(r'<table class="no_columns">(.*?)</table>',
                    re.DOTALL)
    ads = re.findall(rx, page)
    return ads

def merge_two_dicts(x, y):
    '''Funkcija, ki iz dveh slovarjev naredi enega'''
    z = x.copy()   
    z.update(y)    
    return z

def get_data_from_string(directory, filename):
    '''Izlušči podatke o za dano sezono in vrne seznam slovarjev za igralca v tej sezoni'''
    page = read_file_to_string(directory, filename)
    whole_list_of_dicts = []
    for add in page_to_ads(page):
        rt = re.compile(r'<caption>(?P<stevilka>[0-9]{1,2})</caption>')
        rx = re.compile(r'.*?href="(?P<href>/players/[a-z]/[a-z]{5,10}0[1-9])\.html">(?P<ime>.+?)</a>'
                        r'.*?<a href="/teams/[A-Z]+/(?P<konec_sezone>.+?)\.html">(?P<ekipa>.+?)</a>',
                        re.DOTALL)
        data = re.search(rt, add)
        ad_dict = data.groupdict()
        for match in rx.finditer(add):
            dict = merge_two_dicts(match.groupdict(), ad_dict)
            whole_list_of_dicts.append(dict)
    return whole_list_of_dicts


def get_all_the_data(directory):
    '''Funkcija, ki shrani podatke za vse številke dresov'''
    vsi = []
    for leto in range(1965,2019):
        ime_datoteke = "stevilke_dresov_{}_html".format(leto)
        vsi += get_data_from_string(directory, ime_datoteke)
    return vsi


#=============================== CSV =======================================

podatki = get_all_the_data(stevilke_dresov_directory)


def zapisi_csv(podatki, ime_datoteke):
    '''Zapiše csv datoteko za številke dresov'''
    with open(ime_datoteke, 'w', newline='') as datoteka:
        polja = ['ime', 'konec_sezone', 'ekipa', 'stevilka'] #tu sezona pomeni zadnje leto (npr. 2018 če gre za sezono 2017-2018)
        pisalec = csv.DictWriter(datoteka, polja, extrasaction='ignore')
        pisalec.writeheader()
        for igralec in podatki:
            pisalec.writerow(igralec)


#=========== POBIRANJE ŠE PODATKOV O POSAMEZNEM IGRALCU ======================

def clear_hrefs(data):
    '''Funkcija počisti hrefe, da je vsak href samo enkrat.'''
    sez = []
    for igralec in data:
        url = 'https://www.basketball-reference.com{}.html'.format(igralec['href'])
        if url not in sez:
            sez.append(url)
    return sez

def save_frontpages_part2():
    '''Shrani "stevilke_dresov_url" to the file
    "stevilke_dresov_directory"/"podatki_stevilke_html"'''
    razlicni = clear_hrefs(podatki_igralci)
    i = 1
    for url in razlicni:
        ime_datoteke = 'igralec_{}_html'.format(i)
        text = download_url_to_string(url)
        save_string_to_file(text, igralci_directory, ime_datoteke)
        i += 1
    return None

#===============================================================================

def get_data_from_string_part2(directory, filename):
    '''Izlušči podatke o posameznem igralcu.'''
    page = read_file_to_string(directory, filename)
    rt = re.compile(r'.*?<h1.itemprop="name">(?P<ime>.*?)</h1>'
                    r'.*?lb</span>&nbsp;\((?P<visina>[0-9]{3})cm,&nbsp;(?P<teza>[0-9]{2,3})kg'
                    r'.*?data-birth="(?P<leto_rojstva>[0-9]{4})-(?P<mesec_rojstva>[0-9]{2})-(?P<dan_rojstva>[0-9]{2})"'
                    r'.*?>PTS</h4><p>([0-9]{1,2}\.[0-9])?</p>.<p>(?P<povprecje_tocke>([0-9]{1,2}\.[0-9])?)'
                    r'.*?>TRB</h4><p>([0-9]{1,2}\.[0-9])?</p>.<p>(?P<povprecje_skoki>([0-9]{1,2}\.[0-9])?)'
                    r'.*?>AST</h4><p>([0-9]{1,2}\.[0-9])?</p>.<p>(?P<povprecje_asistence>([0-9]{1,2}\.[0-9])?)',
                    re.DOTALL)
    data = re.search(rt, page)
    ad_dict = data.groupdict()
    return ad_dict

#get_data_from_string_part2(igralci_directory, 'igralec_3370_html')

def get_all_the_data_part2(directory):
    '''Funkcija, ki preveri vse igralce. Izpusti zgolj igralce za katere ni podatkov
    (npr. "dunkerje" ter igralce, ki so v nba prišli to sezono)'''
    vsi = []
    for i in range(1, 645):
            ime_datoteke = "igralec_{}_html".format(i)
            vsi.append(get_data_from_string_part2(directory, ime_datoteke)) 
    for i in range(646, 3429):
            ime_datoteke = "igralec_{}_html".format(i)
            vsi.append(get_data_from_string_part2(directory, ime_datoteke)) 
    for i in range(3430, 3468):
        if i not in [3433, 3438, 3440, 3502, 3441, 3445, 3446, 3453, 3457, 3461, 3462, 3464, 3466]:
            ime_datoteke = "igralec_{}_html".format(i)
            vsi.append(get_data_from_string_part2(directory, ime_datoteke))             
    return vsi

#podatki_igralci = get_all_the_data_part2(igralci_directory)

def zapisi_csv_part2(podatki, ime_datoteke):
    '''Zapiše še drugo csv datoteko'''
    with open(ime_datoteke, 'w', newline='', encoding = 'utf8') as datoteka:
        polja = ["ime", "visina", "teza", "leto_rojstva", "mesec_rojstva", "dan_rojstva", "povprecje_tocke", "povprecje_skoki", "povprecje_asistence"]
        pisalec = csv.DictWriter(datoteka, fieldnames=polja)
        pisalec.writeheader()
        for igralec in podatki:
            pisalec.writerow(igralec)
    return None


