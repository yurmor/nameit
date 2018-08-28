# nameit
Extract list of names from an arbitrary html page

Example:

import requests  
from bs4 import BeautifulSoup  

ref = 'https://www.nobelprize.org/prizes/uncategorized/all-nobel-prizes-in-physics/'  
page = requests.get(ref)  
soup = BeautifulSoup(page.text, 'html.parser')  
nmx = Nameit(soup)  
names = nmx.update_names()  
print('Found ', len(names), 'names')   
names.sort()  
pprint(names)  

see more exmaples in example.py
