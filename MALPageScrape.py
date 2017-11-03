# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 22:42:36 2017

@author: Eric
"""

#GOAL: given a MyAnimeList (MAL) TV series page:
#Check if the show is completed.  If it is, then get all of the information


import requests
from bs4 import BeautifulSoup as bsoup
import re
from datetime import datetime as date

#Scrapes a MALPAge for all relevant things, then puts it into a list
class MALPageScrape:
    def __init__(self, url):
        url = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}).content
        self.html = bsoup(url, "lxml")
        
        #airing status, only grab complete ones
        status = self.GetText("Status:")
        
        #only bother doing things if it is finished airing
        if status == "Finished Airing":
        
            media = self.GetText("Type:") # TV / OVA / Movie / Etc
            title = self.html.find('span', attrs={'itemprop' : 'name'}).get_text()  # Title
            eps = self.GetText("Episodes:") # Episodes
            
            # Starting Season
            premiered = self.GetText("Premiered:")
            premiered = premiered.split(' ')
            start_season = premiered[0]
            start_year = premiered[1]
            
            broadcast = self.GetText("Broadcast:") # Broadcast time/day of week
            
            if broadcast == 'Not scheduled once per week' or broadcast == 'Unknown':
                day = ''
                time = ''
                
            else:
                # additional stripping
                broadcast = broadcast.replace('(JST)','')
                broadcast = broadcast.strip(' ')
                broadcast = broadcast.split(' at ')
                
                
                # breaking it down into timeslot and day of the week
                day = broadcast[0]
                time = broadcast[1]
                
                if time == 'Unknown':
                    time = ''
            
            # Producers
            producer_list = self.GetText("Producers:")
            producer_list = re.sub(r"\s+", "", producer_list, flags=re.UNICODE)
            
            # Licensors
            licensor_list = self.GetText("Licensors:")
            if 'None found' in licensor_list:
                licensor_list = ''
            else:
                licensor_list = re.sub(r"\s+", "", licensor_list, flags=re.UNICODE)

            
            # Studios
            studio_list = self.GetText("Studios:").replace(' ', '')
            studio_list = studio_list.replace(' ', '')
            
            # Source Material
            source = self.GetText("Source:")
            source = re.sub(r"\s+", "", source, flags=re.UNICODE)
            
            # Genres
            genres = self.GetText("Genres:")
            genres = genres.replace(' ', '')
            
            # Runtime, more work needed for anything > 1 hr
            runtime = self.GetText("Duration:")
            runtime = runtime.strip("per ep.")
            runtime = runtime.strip('min.')
            
            # Rating (maturity, not score)
            rating = self.GetText("Rating:")
            rating = rating.split(' ')
            rating = rating[0]
            
            # Score
            initial = self.html.find('span', attrs={'itemprop' : 'ratingValue'})
            score = initial.get_text()
            
            members = self.GetText("Members:") # Members
            
            #Is this a sequel? Assume no until we show otherwise
            sequel = 'False'
            previous_score = ''
            previous_pop = ''
            
            initial = self.html.find('td', attrs={'class' : 'ar fw-n borderClass'}, string = 'Prequel:')
            
            if initial != None:
                #scrape it for data
                
                prequel_list = []
                
                check_url_part = initial.find_parent()
                prelim_urls = check_url_part.find_all('a')
                
                
                for row in prelim_urls:
                    prequel_list.append(row.get('href'))

                for i in range(0, len(prequel_list)):
                    check_url = 'https://myanimelist.net' + prequel_list[i]
                    sequel = self.CheckSequel(check_url)
                    
                    if sequel[0] == 'True':
                        previous_score = sequel[1]
                        previous_pop = sequel[2]
                        break #don't check any more of the entries


            
            
            self.master_list = [title, media, eps, start_season, start_year, day, time,  source,  runtime,
                        rating, score, members, previous_score, previous_pop,
                        studio_list, genres,  producer_list, licensor_list]
            
        else:
            #Show not finished
            self.master_list = ['']
            
    ###### HELPER FUNCTIONS ######

    # Shortcut method to a single text response or prepare for a list response
    def GetText(self, name):

        #getting the text from the html
        initial = self.html.find('span', attrs={'class' : 'dark_text'}, string = name)
        parent = initial.find_parent()
        text = parent.get_text()
        
        #basic formatting neatness
        text = text.replace('\n','')
        text = text.replace(name, '')
        text = text.strip(' ')
    
        return text
    
    def CheckSequel(self, url):
        previous_score = ''
        previous_pop = ''
        isSequel = 'False'
        
        search_url = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}).content
                
        new_html = bsoup(search_url, "lxml")
        
        old_start = self.GetText('Aired:')
        old_start = old_start.split(' to ')[0]
        
        new_start = new_html.find('span', attrs={'class' : 'dark_text'}, string = 'Aired:')
        new_start = new_start.find_parent()
        new_start = new_start.get_text()
        new_start = new_start.split(' to ')[0]
        
        new_start = new_start.replace('\n','')
        new_start = new_start.replace('Aired:', '')
        new_start = new_start.strip(' ')
    
        
        if date.strptime(old_start, '%b %d, %Y') > date.strptime(new_start, '%b %d, %Y'):
            isSequel = 'True'
            #Get previous show popularity and rating
            initial = new_html.find('span', attrs={'itemprop' : 'ratingValue'})
            previous_score = initial.get_text()
            
            initial = new_html.find('span', attrs={'class' : 'dark_text'}, string = 'Members:')
            parent = initial.find_parent()
            text = parent.get_text()
        
            #basic formatting neatness
            text = text.replace('\n','')
            text = text.replace('Members:', '')
            previous_pop = text.strip(' ')
            
            
        return [isSequel, previous_score, previous_pop]
