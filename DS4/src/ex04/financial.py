#!/usr/bin/env python3
import sys
from bs4 import BeautifulSoup
import requests
import re
import time

if __name__ == "__main__":
    main_url = f'https://finance.yahoo.com/quote/{sys.argv[1]}/financials/?p={sys.argv[2]}'
    
    
    res = requests.get(
        main_url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/'
        }
    )
    soup = BeautifulSoup(res.text,'html.parser')
    text = 'Total Revenue'
    
    div_bs4 = soup.find('div',class_="row lv-0 yf-t22klz").text
    h = div_bs4.split(' ')
    h[2] = h[2] + ' ' + h[3]
    del h[3]
    k = tuple(i for i in h[2:-1])
    print(k)
