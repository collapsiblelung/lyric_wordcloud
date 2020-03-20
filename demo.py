#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 21:25:36 2020

@author: nicolehunkeapillar

demo.py

Demo of lyric_wordcloud.py
"""


from lyric_wordcloud import generate_wordcloud


if __name__ == '__main__':
    artist = 'Relient K'
    file = './demo/rk.csv'
    text_color = (154, 205, 184) # mint green candy hearts ep
    bg_img = './demo/rk-bw.jpg'
    
    most_used, one_str, request_times = generate_wordcloud(file, artist, text_color, bg_img)
    
    artist = 'Switchfoot'
    file = './demo/sf_j4.csv'
    text_color = (251, 228, 76) # yellow native tongue
    bg_img = './demo/sf-bw.jpg'
    
    most_used, one_str, elapsed = generate_wordcloud(file, artist, text_color, bg_img)