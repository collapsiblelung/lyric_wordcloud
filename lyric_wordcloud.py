#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 17:37:25 2019

@author: nhunkeapillar
"""

# modified getLinks definition from 
# https://pythonspot.com/extract-links-from-webpage-beautifulsoup/

# lyrics retrieved from genius.com

from lxml import html
import time
import requests
from itertools import chain
from string import punctuation
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from wordcloud import WordCloud
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re


text_color = (154, 205, 184) # rk mint green
(251, 228, 76) # native tongue yellow


def remove_values_from_list(the_list, vals):
    for val in vals:
        while val in the_list:
            the_list.remove(val)
  
  
def getLinks(url):
    html_page = urlopen(url)
    soup = BeautifulSoup(html_page, 'html.parser')
    links = []
    
    for page in soup.findAll('a', attrs={'class': 'btn btn-share btn-nav'}):
        songs_page = urlopen(url)
        soup = BeautifulSoup(songs_page, 'html.parser')
        
        for link in soup.findAll('a', attrs={'href': re.compile("^https://")}):
            links.append(link.get('href'))
            
    
    links = sorted(set(links))
 
    return links


def wordcloud(file, artist, bg_image):
    data = pd.read_csv(file)
    data = data[data['Artist'].str.find(artist) != -1]
    data = data.drop_duplicates(subset='Song', keep='first')
    data = data.sort_values(by=['Artist', 'Year', 'Album', 'Track Number'])
    songs = data['Song']
    base_url = 'https://genius.com/%s-' % artist.replace(' ', '-').lower()
    pages = [base_url + '-'.join(song.lower().split()) + '-lyrics' for song in songs]
    #links = getLinks('https://search.azlyrics.com/search.php?q=%s&w=songs' % artist)
    all_words, request_times = [], []
    i = 0
    
    for song, page in zip(songs, pages):
        try:
            response = requests.get(page)
            time.sleep(1)
            request_times.append(time.time())
        except:
            print('Failed on %s' % song)
            continue
        
        tree = html.fromstring(response.content)
        words = tree.xpath('//p/text()')
        words = [x.strip() for x in words if x.find('[') == -1]
        
        if words == ["Sorry, we didn't mean for that to happen!", 
                     'You can search Genius by using the search bar above, or', 
                     '.']:
            continue
        
        words = list(set(chain.from_iterable([x.split() for x in words])))
        all_words.append(words)
        print('done with song %d - %s' % (i+1, song))
        i += 1
        
    print('processed %d songs' % i)
    all_words = list(chain.from_iterable(all_words))
    all_words = [x.lower() for x in all_words]
    
    c = Counter(all_words)
    most_used = c.most_common(500)
    one_str = ' '.join(all_words)
    
    mask = np.array(Image.open(bg_image))
#    image_colors = ImageColorGenerator(mask)
    plt.figure()
    wordcloud = WordCloud(max_font_size=200, max_words=1000, 
                          background_color=None,
                          mask=mask, mode='RGBA',
                          color_func=lambda *args, **kwargs: text_color).generate(one_str)
    plt.imshow(wordcloud, interpolation='bilinear') # .recolor(color_func=image_colors)
    plt.axis('off')
    wordcloud.to_file('%s_wordcloud.png' % artist)
    
    return most_used, one_str, request_times



if __name__ == '__main__':
    artist = 'Relient K'
    file = 'rk.csv'
    bg_img = '2017.jpg'
    most_used, one_str, request_times = wordcloud(file, artist, bg_img)
