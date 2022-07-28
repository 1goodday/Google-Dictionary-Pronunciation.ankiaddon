# from aqt.utils import showInfo
from anki.hooks import addHook
import os
from aqt import gui_hooks, mw
from anki.cards import Card
from anki import collection
import re
import requests
# from fake_useragent import UserAgent
# import webbrowser
# from selenium import webdriver


def extract_pron_url(url):
    begin_str = "//ssl.gstatic.com/dictionary/static/"
    end_str = ".mp3"

    ua = UserAgent()

    my_headers = {
    'User-Agent': ua.chrome #'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    html = requests.get(url, headers = my_headers)
    print(begin_str in html.text)
    print(end_str in html.text)

    file1 = open("html.html","wb")
    file1.write(html.content)
    file1.close()

    all_matches =  re.findall("%s.{0,80}%s" % (begin_str, end_str), html.text)
 

    return "http:" + min(all_matches, key=len)




word_search_url = "https://www.google.com/search?q=definition:" + 'cob'
pron_url = extract_pron_url(word_search_url)
print(pron_url)
