#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Sat Jan 19 17:37:25 2019

@author: nhunkeapillar

Lyrics retrieved from genius.com.
'''

from lxml import html
import time
import requests
from itertools import chain
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from wordcloud import WordCloud, ImageColorGenerator
from bs4 import BeautifulSoup
from urllib.request import urlopen
from string import punctuation
import re


def remove_values_from_list(the_list, vals):
    ''' Removes each value in values from the the_list.'''
    for val in vals:
        while val in the_list:
            the_list.remove(val)
  
  
def get_links(url):
    '''
    Gets all links for a given webpage.

    Parameters
    ----------
    url : STRING
        Url of webpage to get links from.

    Returns
    -------
    links : LIST
        List of link strings contained in url.

    '''
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


def generate_wordcloud(file, artist, text_color, bg_image, recolor=False):
    '''
    Creates a wordcloud from an artist's data from an iTunes library.

    Parameters
    ----------
    file : STRING
        Path to csv file containing an Artist's data (columns must 
        include Artist, Year, Album, and Track Number at a minimum).
        At present, to create this file requires user to open iTunes, 
        go to Songs (detailed view), and Ctrl+A copy to a file.
    artist : STRING
        Artist you want to use for the word cloud.
    text_color : TUPLE
        RGB tuple color value.
    bg_image : STRING
        Path to image used in the background of the word cloud.
    recolor : BOOLEAN, default False
        If True, colors text in word cloud based on colors in bg_image.
        If False, uses text_color for all words.

    Returns
    -------
    most_used : LIST
        Tuples of the 500 most commonly found words and their count, ranked
        by count.
    one_str : STRING
        All words used in single string.
    elapsed : FLOAT
        Total amount of time it took the function to run in seconds.

    '''
    start_time = time.time()
    data = pd.read_csv(file)
    data = data[data['Artist'].str.find(artist) != -1]
    data = data.drop_duplicates(subset='Song', keep='first')
    data = data.sort_values(by=['Artist', 'Year', 'Album', 'Track Number'])
    songs = data['Song']
    base_url = 'https://genius.com/%s-' % artist.replace(' ', '-').lower()
    pages = [base_url + '-'.join(song.lower().split()) + '-lyrics' for song in songs]
    all_words = []
    i = 0
    
    for song, page in zip(songs, pages):
        try:
            response = requests.get(page)
            time.sleep(1)
        except:
            print('Failed on %s.' % song)
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
        print('Done with song %d - %s' % (i+1, song))
        i += 1
        
    print('Processed %d songs' % i)
    all_words = list(chain.from_iterable(all_words))
    all_words = [x.lower() for x in all_words]
    table = str.maketrans('', '', punctuation)
    all_words = [w.translate(table) for w in all_words]
    
    c = Counter(all_words)
    most_used = c.most_common(500)
    one_str = ' '.join(all_words)
    
    mask = np.array(Image.open(bg_image))

    plt.figure()
    
    if recolor:
        image_colors = ImageColorGenerator(mask)
        wordcloud = WordCloud(max_font_size=200, max_words=1000, 
                          background_color=None,
                          mask=mask, mode='RGBA',
                          color_func=lambda *args, **kwargs: text_color).generate(one_str).recolor(color_func=image_colors)
    else:
        wordcloud = WordCloud(max_font_size=200, max_words=1000, 
                              background_color=None,
                              mask=mask, mode='RGBA',
                              color_func=lambda *args, **kwargs: text_color).generate(one_str)
    
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    wordcloud.to_file('%s_wordcloud.png' % artist)
    
    end_time = time.time()
    elapsed = end_time - start_time
    print('Elapsed time: %d s\n' % elapsed)
    
    return most_used, one_str, elapsed



if __name__ == '__main__':
    artist = 'Relient K'
    file = 'rk.csv'
    text_color = (154, 205, 184) # mint green candy hearts ep
    bg_img = '2017.jpg'
    
    most_used, one_str, request_times = generate_wordcloud(file, artist, text_color, bg_img)
    
    artist = 'Switchfoot'
    file = 'sf_j4.csv'
    text_color = (251, 228, 76) # yellow native tongue
    bg_img = 'nt.jpg'
    
    most_used, one_str, elapsed = generate_wordcloud(file, artist, text_color, bg_img)
    