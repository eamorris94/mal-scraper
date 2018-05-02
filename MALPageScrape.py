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

def GetText(html, name):
    #getting the text from the html
    initial = html.find('span', attrs={'class' : 'dark_text'}, string = name)
    parent = initial.find_parent()
    text = parent.get_text()
        
    #basic formatting neatness
    text = text.replace('\n','')
    text = text.replace(name, '')
    text = text.strip(' ')
    
    return text

#Scrapes a MALPAge for all relevant things, then puts it into a list
class MALPageScrape:
    def __init__(self, url):
        
        #headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}
        response = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}).content
        self.html = bsoup(response, "lxml")
        
        #airing status, only grab complete ones
        status = GetText(self.html, "Status:")
        
        #only bother doing things if it is finished airing
        if status == "Finished Airing":
        
            media = GetText(self.html, "Type:") # TV / OVA / Movie / Etc
            title = self.html.find('span', attrs={'itemprop' : 'name'}).get_text()  # Title
            eps = GetText(self.html, "Episodes:") # Episodes
            
            # Starting Season
            premiered = GetText(self.html, "Premiered:")
            premiered = premiered.split(' ')
            
            #will only go to except if information is unknown
            try:
                start_season = premiered[0]
                start_year = premiered[1]
            except:
                start_season = "NA"
                start_year = "NA"
            
            broadcast = GetText(self.html, "Broadcast:") # Broadcast time/day of week
            
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
            producer_list = GetText(self.html, "Producers:")
            producer_list = re.sub(r"\s+", "", producer_list, flags=re.UNICODE)
            
            # Licensors
            licensor_list = GetText(self.html, "Licensors:")
            if 'None found' in licensor_list:
                licensor_list = ''
            else:
                licensor_list = re.sub(r"\s+", "", licensor_list, flags=re.UNICODE)

            
            # Studios
            studio_list = GetText(self.html, "Studios:").replace(' ', '')
            studio_list = studio_list.replace(' ', '')
            
            # Source Material
            source = GetText(self.html, "Source:")
            source = re.sub(r"\s+", "", source, flags=re.UNICODE)
            
            # Genres
            genres = GetText(self.html, "Genres:")
            genres = genres.replace(' ', '')
            
            # Runtime, more work needed for anything > 1 hr
            runtime = GetText(self.html, "Duration:")
            runtime = runtime.strip("per ep.")
            runtime = runtime.strip('min.')
            
            # Rating (maturity, not score)
            rating = GetText(self.html, "Rating:")
            rating = rating.split(' ')
            rating = rating[0]
            
            # Score
            initial = self.html.find('span', attrs={'itemprop' : 'ratingValue'})
            score = initial.get_text()
            
            members = GetText(self.html, "Members:") # Members
            
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

                #catching a specific error.  not sure why it is happening.
                if prequel_list == ['/anime//']:
                    prequel_list = []
                
                for i in range(0, len(prequel_list)):
                    check_url = 'https://myanimelist.net' + prequel_list[i]
                    sequel = self.CheckSequel(check_url)
                    
                    if sequel[0] == 'True':
                        previous_score = sequel[1]
                        previous_pop = sequel[2]
                        break #don't check any more of the entries


            #Get IDs!

            #main voice actors, followed by director(s)
            general_blocks = self.html.find_all('div', attrs={'class' : 'left-column fl-l divider'})
            va_list = ''
            dir_list = ''
            
            try:
                va_block = general_blocks[0].parent
                isVA = False
                
                #get all of the main VAs, then end when there are no more of them
                for string in va_block.stripped_strings:
                    if isVA == True:
                        va_list = va_list + '|' + string
                        isVA = False
                    elif string == 'Supporting':
                        break
                    elif string == 'Main':
                        isVA = True            
                
                # Director
                dir_block = general_blocks[1].parent
                temp = ''
                
                for string in dir_block.stripped_strings:
                    if string == 'Director' or 'Director, ' in string or ', Director' in string:
                        dir_list = dir_list + '|' + temp
                    else:
                        temp = string
            except:
                pass
            
            source_url = ''
            source_type = ''
            source_score = ''
            source_pop = ''
            
            try:
                
                if source != 'Original':
                    search = self.html.find('td', attrs={'class' : 'ar fw-n borderClass'}, string = "Adaptation:")
                    par = search.parent
                    url = par.find('a')
                    
                    source_url = url.get('href')                    
                    search_url = 'https://myanimelist.net'+ source_url
                    search_url = requests.get(search_url, headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}).content
                    search_html = bsoup(search_url, "lxml")
                    
                    s_release = GetText(search_html, 'Published:')
                    s_release = s_release.split(' to ')
                    s_release = s_release[0]
                    
                    a_release = GetText(self.html, 'Aired:')
                    a_release = a_release.split(' to ')
                    a_release = a_release[0]
                    
                    s_release = s_release.replace('  ', ' ')
                    if s_release != 'Not available':
                    
                        try:
                            # only continue if the source predates the original
                            if date.strptime(s_release, '%b %d, %Y') > date.strptime(a_release, '%b %d, %Y'):
                                pass
                                
                            else:
                                # get score, popularity, and type
                                source_type = GetText(search_html, 'Type:')
                                source_score = search_html.find('span', attrs={'itemprop' : 'ratingValue'})
                                source_score = source_score.get_text()
                                source_pop = GetText(search_html, 'Members:')
                                
                        #try using only release month        
                        except ValueError:
                            try:
                                if date.strptime(s_release, '%b %Y') > date.strptime(a_release, '%b %d, %Y'):
                                    pass
                                    
                                else:
                                    # get score, popularity, and type
                                    source_type = GetText(search_html, 'Type:')
                                    source_score = search_html.find('span', attrs={'itemprop' : 'ratingValue'})
                                    source_score = source_score.get_text()
                                    source_pop = GetText(search_html, 'Members:')
                            except ValueError:
                                
                                if date.strptime(s_release, '%Y') > date.strptime(a_release, '%b %d, %Y'):
                                    pass
                                    
                                else:
                                    # get score, popularity, and type
                                    source_type = GetText(search_html, 'Type:')
                                    source_score = search_html.find('span', attrs={'itemprop' : 'ratingValue'})
                                    source_score = source_score.get_text()
                                    source_pop = GetText(search_html, 'Members:')
                                
            except AttributeError:
                source_url = ''
                
            self.master_list = [title, media, eps, start_season, start_year, day, time,  source,  runtime,
                        rating, score, members, previous_score, previous_pop, source_url, source_type, 
                        source_score, source_pop, dir_list[1:], va_list[1:], studio_list, genres,  producer_list, licensor_list]
            
            for i in range(0, len(self.master_list)):
                if self.master_list[i] == None:
                    self.master_list[i] = ''
                    
                    
        else:
            #Show not finished
            self.master_list = ['']
            
    ###### HELPER FUNCTIONS ######
    
    def CheckSequel(self, url):
        previous_score = ''
        previous_pop = ''
        isSequel = 'False'
        
        search_url = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}).content
                
        new_html = bsoup(search_url, "lxml")
        
        old_start = GetText(self.html, 'Aired:')
        old_start = old_start.split(' to ')[0]
        
        new_start = GetText(new_html, 'Aired:')
        new_start = new_start.split(' to ')[0]
        
        try:
            if date.strptime(old_start, '%b %d, %Y') > date.strptime(new_start, '%b %d, %Y'):
                isSequel = 'True'
                #Get previous show popularity and rating
                initial = new_html.find('span', attrs={'itemprop' : 'ratingValue'})
                previous_score = initial.get_text()
                
                previous_pop = GetText(new_html, 'Members:')
                
        except ValueError:
            try:
                if date.strptime(old_start, '%b %d, %Y') > date.strptime(new_start, '%Y'):
                    isSequel = 'True'
                    #Get previous show popularity and rating
                    initial = new_html.find('span', attrs={'itemprop' : 'ratingValue'})
                    previous_score = initial.get_text()
                    
                    previous_pop = GetText(new_html, 'Members:')
                    
            except ValueError:
                if date.strptime(old_start, '%Y') > date.strptime(new_start, '%b %d, %Y'):
                    isSequel = 'True'
                    #Get previous show popularity and rating
                    initial = new_html.find('span', attrs={'itemprop' : 'ratingValue'})
                    previous_score = initial.get_text()
                    
                    previous_pop = GetText(new_html, 'Members:')
                
            
        return [isSequel, previous_score, previous_pop]











