from __future__ import absolute_import, unicode_literals
import time
import urllib.request
import urllib.parse

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import bs4 as BeautifulSoup



import time


#from celery.decorators import task
from celery import shared_task

@shared_task
def testCeleryFunction():
    print('rororoorororororo - start')
    time.sleep(5)
    print('rororoorororororo - end')


# Celery tasks
@shared_task
def celeryWebMiner(url):
    soup = getSoup(url) 
    temp = getSoupInfo(soup)
    print(temp)
    print(temp) 





def getUrlData(url):
    response_raw_data = ""
    try:
        response = urllib.request.urlopen(url, timeout = 10)
        response_raw_data = response.read()
    except urllib.request.URLError as e:
        raise MyException("There was an error: %r" % e)
    except :
        pass

    return response_raw_data

def getSoup(target_url):
    try :
        raw_url_data = getUrlData(target_url)
        soup = BeautifulSoup.BeautifulSoup(raw_url_data, 'html.parser')
    except :
        soup = BeautifulSoup.BeautifulSoup(str(), 'html.parser')
    return soup

def getSoupInfo(soup, source_url):
    temp = dict()
    temp["favicon_url"] = ''
    temp["image_url"] = ''
    temp["title"] = ''
    temp["description"] = ''

    # FAVICON
    if soup.find("link", rel="shortcut icon") :
        icon_link = soup.find("link", rel="shortcut icon")
        val = URLValidator()
        try:
            val(icon_link["href"])
            temp["favicon_url"] = icon_link['href']
        except ValidationError as e:
            pass

    # TITLE
    if soup.find("meta",  property="og:title") :
        title = soup.find("meta",  property="og:title")
        temp["title"] = title["content"]
        #print(title["content"])
    elif soup.find('title') :
        #print(soup.find('title'))
        temp["title"] =  soup.find('title').text

    # DESCRIPTION
    if soup.find("meta",  property="og:description") :
        url_description = soup.find("meta",  property="og:description")
        # verify text encoding, maybe remove consecutive /n ?
        temp["description"] = url_description["content"]

    # MAIN IMAGE URL
    if soup.find("meta",  property="og:url") :
        url = soup.find("meta",  property="og:url")
        val = URLValidator()
        try:
            val(url["content"])
            temp["image_url"] = url["content"]
        except ValidationError as e:
            pass

    try :
        title = soup.find("meta",  property="og:title")
        temp["title"] = title["content"]
    except :
        pass
    try :
        url = soup.find("meta",  property="og:url")
        temp["image_url"] = img_url["content"]
    except :
        pass
    try :
        url_description = soup.find("meta",  property="og:description")
        temp["description"] = url_description["content"]
    except :
        pass

    return temp

#@task(name="celery_mine_url")
@shared_task
def retrieveUrlContent(bookmark_object):
#RETRIEVE RAW HTML AND GENERATE RETRIEVED DATA TEMP DICT$
    a = 0
    url =  bookmark_object["url"]
    soup = getSoup(url)
    html = getSoupInfo(soup, url)

    bookmark_object["favicon_url"] = html["favicon_url"]
    bookmark_object["title"] = html["title"]
    bookmark_object["description"] = html["description"][:250].replace('\n', ' ')
    # bookmark_object["image_url"] = html["image_url"] // TODO: check if it works
    return bookmark_object

common_words = ["the", "be", "and", "of", "a", "in", "to", "have", "it", "I", "that", "for", "you", "do", "on", "say", "",]
nltk_default_tag = ['AT', 'NN', 'VB', 'JJ', 'IN', 'CD', 'END']
