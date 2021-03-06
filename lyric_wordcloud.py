#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Sat Jan 19 17:37:25 2019

@author: nhunkeapillar

Lyrics retrieved from genius.com.
'''

import re
import os
import time
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from string import punctuation
from lxml import html
from itertools import chain
from collections import Counter
from PIL import Image
from urllib.request import urlopen
from bs4 import BeautifulSoup
from wordcloud import WordCloud, ImageColorGenerator


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
        Path to image later used in the background of the word cloud.
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
    
    save_dir = os.path.join('.', 'clouds')
    if not os.path.isdir(save_dir): os.makedirs(save_dir)
    
    data = pd.read_csv(file)
    data = data[data['Artist'].str.find(artist) != -1]
    data = data.drop_duplicates(subset='Song', keep='first')
    data = data.sort_values(by=['Artist', 'Year', 'Album', 'Track Number'])
    songs = data['Song']
    base_url = 'https://genius.com/%s-' % artist.replace(' ', '-').lower()
    pages = [base_url + '-'.join(song.lower().split()) + '-lyrics' for song in songs]
    all_words = []
    
    for i, (song, page) in enumerate(zip(songs, pages)):
        try:
            response = requests.get(page)
            time.sleep(0.5)
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
        
    print('Processed %d songs' % i)
    all_words = list(chain.from_iterable(all_words))
    all_words = [x.lower() for x in all_words]
    table = str.maketrans('', '', punctuation)
    all_words = [w.translate(table) for w in all_words]
    
    c = Counter(all_words)
    most_used = c.most_common(500)
    one_str = ' '.join(all_words)
    
    mask = np.array(Image.open(bg_image))

    fig, ax = plt.subplots()
    
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
    
    ax.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    wordcloud.to_file(os.path.join(save_dir, '%s_wordcloud.png' % artist))
    
    end_time = time.time()
    elapsed = end_time - start_time
    print('Elapsed time: %d s\n' % elapsed)
    
    return most_used, one_str, elapsed


if __name__ == '__main__':
    pass
    