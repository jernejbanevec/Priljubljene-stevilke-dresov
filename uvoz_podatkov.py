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
#NA FAKSU
#stevilke_dresov_directory = 'U:/Programiranje1\Priljubljene-stevilke-dresov\Podatki'

# ime CSV datoteke s podatki
podatki_stevilke_dresov_csv = "podatki.csv"
podatki_stevilke_dresov_csv2 = "podatki1.csv"
# filepage
#frontpage_filename = "stevilke_dresov_1965_html"


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
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def get_data_from_string(directory, filename):
    '''Izlušči podatke.'''
    page = read_file_to_string(directory, filename)
    whole_list_of_dicts = []
    for add in page_to_ads(page):
        rt = re.compile(r'<caption>(?P<stevilka>[0-9]{1,2})</caption>')
        rx = re.compile(r'.*?"/players/[a-z]/[a-z]{5,10}0[1-9]\.html">(?P<ime>.+?)</a>'
                        r'.*?<a href="/teams/[A-Z]+/(?P<konec_sezone>.+?)\.html">(?P<ekipa>.+?)</a>',
                        re.DOTALL)
        data = re.search(rt, add)
        ad_dict = data.groupdict()
        for match in rx.finditer(add):
            dict = merge_two_dicts(match.groupdict(), ad_dict)
            whole_list_of_dicts.append(dict)
    return whole_list_of_dicts


def get_all_the_data(directory):
    vsi = []
    for leto in range(1965,2019):
        ime_datoteke = "stevilke_dresov_{}_html".format(leto)
        vsi += get_data_from_string(directory, ime_datoteke)
    return vsi

#=============================== CSV =======================================

podatki_igralci = get_all_the_data(stevilke_dresov_directory)

def zapisi_csv(podatki, ime_datoteke):
    with open(ime_datoteke, 'w', newline='') as datoteka:
        polja = ['ime', 'konec_sezone', 'ekipa', 'stevilka']
        pisalec = csv.DictWriter(datoteka, polja)
        #pisalec.writeheader()
        for igralec in podatki:
            pisalec.writerow(igralec)
