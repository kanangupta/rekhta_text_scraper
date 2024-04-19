import time
from bs4 import BeautifulSoup
from tqdm import tqdm
import urllib.request
import requests
import os
import pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('begin', type=int, help='beginning index in the list of authors')
parser.add_argument('end', type=int, help='last index in the list of authors')
args = parser.parse_args()


#captures the different <p> tags as newlines
def text_with_newlines(elem):
    text = ''
    for e in elem.descendants:
        if isinstance(e, str):
            text += e
        elif e.name == 'br' or e.name == 'p':
            text += '\n'
    return text


def parse_ghazal(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    mydivs = soup.find_all("div", {"class": "pMC"})  # Find all instances of the pMC class
    
    # Check if there is at least one instance of pMC class
    if mydivs:        
        # Remove English translations present on the webpage
        for div in mydivs[1].find_all("div", {'class': 't'}):
            div.decompose()
        
        return text_with_newlines(mydivs[1])


#Loading the file containing the links to all the ghazals on Rekhta
#The file was created using th Jupyter notebook in this repository
with open('ghazal_links.pk', 'rb') as file:
    dataset=pickle.load(file)
authors = list(dataset.keys())

lang='hi' #can be 'en', 'ur', or 'hi'
begin = args.begin
end = args.end
failed = []
for auth in authors[begin:end]:
    try:
        ghazals = []
        print(f'scraping ghazals of {auth}')
        for url in tqdm(dataset[auth]):
            if lang!='en':
                url = url+'?lang='+lang
            ghazals.append(parse_ghazal(url).lstrip("\n"))
        with open(f'ghazals_{lang}/{auth}_{lang}.txt', 'w', encoding='utf-8') as file:
            file.write("\n\n".join(ghazals))
    except Exception as e:
        print(e)
        print("Failed:",auth)
        failed.append(auth)
with open(f'failed_{begin}-{end}.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(failed))