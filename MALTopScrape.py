# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 10:56:56 2017

@author: Eric
"""

import requests
import csv

from bs4 import BeautifulSoup as bsoup
from MALPageScrape import MALPageScrape as scrape

#TODO: put this in a class-like structure for calling by other programs
#TODO: make sure this works

# this times 50 = top x shows to be considered
class MALTopScrape:
    def __init__(self):
        with open("MALtext2.csv", "wb") as f:
            writer = csv.writer(f)
            #Put in a header row
            writer.writerow(['Title', 'Type', 'Eps', 'Season', 'Year', 'Day', 'Timeslot', 'Source','Runtime', 'Rating',
                            'Score', 'Popularity', 'Sequel Score', 'Sequel Popularity', 'Studio', 'Genres', 'Producers', 'Licensors'])
            
            
            for z in range(0, 1):
                base_url = 'https://myanimelist.net/topanime.php?type=tv'
                search_url = base_url + '&limit=' + str(z * 50)
                response = requests.get(search_url, headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}).content
                            
                
                #parse the results
                parsed_html = bsoup(response, "lxml")
                prelim_list = parsed_html.find_all('a', attrs = {'class':'hoverinfo_trigger fl-l fs14 fw-b'})
                
                
                url_list = []
                
                #get the urls from the table, don't scrape anything with less than 10k members
                #also not scraping from series that started before 2000
                #arbitrary boundary to remember for what is notable.
                for row in prelim_list:
                    check = row.find_parent()
                    check = check.find_next_sibling('div')
                    check = check.get_text()
                    check = check.split('\n')
                    
                    year = check[2]
                    year = year.split('-')[0]
                    year = year.strip(' ')
                    year = year[4:] 
                    
                    popularity = check[3]
                    popularity = popularity.replace(' members', '')
                    popularity = popularity.replace(',', '')
    
                    if int(popularity) >= 10000 and year >= '2000':
                        url_list.append(row.get('href'))
                    
                #scrape each of the urls and write to file
                for i in range(0, len(url_list)):
                    x = scrape(url_list[i])
                    row = [s.encode('utf-8') for s in x.master_list]
                    if row != ['']:
                        writer.writerows([row])
                
        f.close()            
                