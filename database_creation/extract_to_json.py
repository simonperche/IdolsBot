"""
Extraction of kpop idol

    This script extract and store in JSON file kpop idols from KPopping website (https://kpopping.com).
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

import requests
from bs4 import BeautifulSoup


def main():
    r = requests.get('https://kpopping.com/profiles/the-idols')
    soup = BeautifulSoup(r.text, 'html.parser')
    idol_id = 0

    # Dictionary with the id as key and all information (name, groups, img_url...) in dictionary as value
    # Entries (all fields are mandatory):
    #   url         string
    #   name        string
    #   groups      List of strings
    #   img_url     List of strings
    #
    idols = {}

    for e in soup.findAll('div', {'class': 'idol'}):
        if e.find('a'):
            url = 'https://kpopping.com' + e.find('a')['href']
            print(url)

            r = requests.get(url)
            idol_page = BeautifulSoup(r.text, 'html.parser')

            name = idol_page.find('h1').text.rstrip()
            images_url = []

            for img in idol_page.findAll('img'):
                if name.lower() in img['alt'].lower() and 'default_silhouette' not in img['data-src']:
                    images_url.append('https://kpopping.com' + img['data-src'])

            if not images_url:
                continue

            groups_name = []

            for a in idol_page.find('div', {'class': 'box-encyclopedia'}).findAll('a'):
                if not a.has_attr('href'):
                    continue

                if 'group' in a['href']:
                    groups_name.append(a.text)

            if not groups_name:
                continue

            idols[idol_id] = {'url': url,
                              'name': name,
                              'groups': groups_name,
                              'img_url': images_url}
            print(idols[idol_id])
            print('\n')

            idol_id += 1

    with open('database.json', 'w') as db:
        json.dump(idols, db)


if __name__ == "__main__":
    main()