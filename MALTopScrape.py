# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 10:56:56 2017

@author: Eric
"""

import requests
import csv

from bs4 import BeautifulSoup as bsoup
from MALPageScrape import MALPageScrape as scrape


# this times 50 = top x shows to be considered
class MALTopScrape:
    def __init__(self):
        with open("animedata4.csv", "wb") as f:
            writer = csv.writer(f)
            #Put in a header row
            writer.writerow(['Title', 'Type', 'Eps', 'Season', 'Year', 'Day', 'Timeslot', 'Source','Runtime', 'Rating',
                            'Score', 'Popularity', 'Sequel Score', 'Sequel Popularity', 'Source Url', 'Source Type',
                            'Source Score', 'Source Pop', 'Directors', 'Main VAs', 'Studio', 'Genres', 'Producers', 'Licensors'])
            
            
            for z in range(0, 75):
                print "working on page: " + str(z)
                base_url = 'https://myanimelist.net/topanime.php?type=tv'
                search_url = base_url + '&limit=' + str(z * 50)
                response = requests.get(search_url).content
                            
                
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
                    
                    target = check[2]
                    target = "".join(_ for _ in target if _ in "1234567890")
                    
                    
                    year = target[:4]
                    popularity = target [8:]
                    
                    #print year
                    #print popularity
                    
                    #old method that worked circa October 2017, but no longer does
                    #year = check[2]
                    #year = year.split('-')[0]
                    #year = year.strip(' ')
                    #year = year[4:] 
                    
                    #popularity = check[3]
                    #popularity = popularity.replace(' members', '')
                    #popularity = popularity.replace(',', '')
    
                    try:
                        if int(popularity) >= 3000 and year >= '1995':
                            url_list.append(row.get('href'))
                    except:
                        pass
                    
                #scrape each of the urls and write to file
                for i in range(0, len(url_list)):
                    #print(url_list[i])
                    #print(type(url_list[i]))
                    x = scrape(url_list[i])
                    row = [s.encode('utf-8') for s in x.master_list]
                    if row != ['']:
                        writer.writerows([row])
                
        f.close()            
                