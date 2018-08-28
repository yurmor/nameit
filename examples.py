from nameit import Nameit
import requests
import bs4
from bs4 import BeautifulSoup
from collections import Counter

if __name__=='__main__':
    # Let's look on list of Nobel Laureates in Physics
    ref = 'https://www.nobelprize.org/prizes/uncategorized/all-nobel-prizes-in-physics/'
    # obtain the page to work with
    page = requests.get(ref)
    soup = BeautifulSoup(page.text, 'html.parser')

    nmx = Nameit(soup)
    names_phys = nmx.update_names()
    names_phys.sort()

    print('Found ', len(names_phys), 'names')
    #let's find how many knights were among nobel laureats in physics
    knights = [nm for nm in names_phys if 'sir' in nm.lower()]

    print('There were ', len(knights), ' knights who received Nobel Prize in Physics')
    print(knights)
    #Now, let's find most popular first names among physics laureats
    name_parts = nmx.assign_first_last_names()
    print('Most popular first names: ')
    print(Counter([x[1] for x in name_parts]).most_common(10))

    print('Most popular last names: ')
    print(Counter([x[2] for x in name_parts]).most_common(9))

    #pprint(nmx.assign_first_last_names())
    
    #What about chemistry? Let's find out who received both Nobel Prize in Chemistry and Physics

    ref = 'https://www.nobelprize.org/prizes/uncategorized/all-nobel-prizes-in-chemistry/'
    # obtain the page to work with
    page = requests.get(ref)
    soup = BeautifulSoup(page.text, 'html.parser')

    nmx = Nameit(soup)
    names_chem = nmx.update_names()
    names_chem.sort()

    print('Found ', len(names_chem), 'names')
    for name in names_chem:
        if name in names_phys:
            print(name)
    # This should return names Alfred Nobel and Marie Curie Sklodowska
    # Alfred Nobel of course did not receive a Nobel Prize, but his name was present on both pages