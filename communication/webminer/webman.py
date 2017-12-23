from __future__ import absolute_import, unicode_literals
import time
import urllib.request
import urllib.parse

import bs4 as BeautifulSoup
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from celery import shared_task

def deconstructUrl(url):
    parsed_uri = urllib.parse(url)
    domain = '''{uri.scheme}://{uri.netloc}/'''.format(uri=parsed_uri)
    return parsed_uri

def getUrlData(url):
    print("Starting webman")
    #print(url)
    response_raw_data = ""
    parsed_url = deconstructUrl(url)
    # print(parsed_url.netloc)

    try:
        response = urllib.request.urlopen(url, timeout = 10)
        response_raw_data = response.read()
    except urllib.request.URLError as e:
        raise MyException("There was an error: %r" % e)
    except :
        print("Error in get url data")

    #print(repr(response_raw_data))
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
    temp["source_url"] = ''
    temp["url_arguments"] = ''




# FAVICON
    if soup.find("link", rel="shortcut icon") :
        icon_link = soup.find("link", rel="shortcut icon")
        val = URLValidator()
        try:
            val(icon_link["href"])
            temp["favicon_url"] = icon_link['href']
        except ValidationError as e:
            #print('e52120')
            #print(e)
            try :
                parsed_url = deconstructUrl(source_url)
                temp_url = str(parsed_url.scheme + "://" + parsed_url.netloc + icon_link['href'])
                val(temp_url)
                temp["favicon_url"] = temp_url
            except ValidationError as e:
                print('e52120')
                #print(str(temp_url))
                print(e)






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

 # URL ARGUMENTS

 # REQUEST RESPONSE


# MAIN IMAGE URL
    if soup.find("meta",  property="og:url") :
        url = soup.find("meta",  property="og:url")
        val = URLValidator()
        try:
            val(url["content"])
            temp["image_url"] = url["content"]
        except ValidationError as e:
            print('e89123')
            print(e)

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




# Celery tasks
#@shared_task
def retrieveUrlContent(bookmark_object):
#RETRIEVE RAW HTML AND GENERATE RETRIEVED DATA TEMP DICT$
    a = 0
    url =  bookmark_object["url"]
    soup = getSoup(url)
    temp = getSoupInfo(soup, url)
# SOURCE URL
    parsed_uri = urllib.parse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    page_document_type = parsed_uri.path.split(".")[len(parsed_uri.path.split("."))-1:]
    bookmark_object["source"] = domain

    bookmark_object["favicon_url"] = temp["favicon_url"]
    bookmark_object["title"] = temp["title"]
    bookmark_object["description"] = temp["description"][:250].replace('\n', ' ')
    return bookmark_object





#import os, sys, json, shutil, csv, subprocess, threading, datetime, requests, random, string

#from django.shortcuts import render
#from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404

#from HTMLParser import HTMLParser
#import numpy as np

#import nltk
#nltk.download("punkt")
#nltk.download("maxent_treebank_pos_tagger")
#nltk.download("averaged_perceptron_tagger")
#from nltk.tokenize import word_tokenize, sent_tokenize, wordpunct_tokenize
#from nltk.corpus import stopwords
#from nltk.tag import pos_tag, map_tag

common_words = ["the", "be", "and", "of", "a", "in", "to", "have", "it", "I", "that", "for", "you", "do", "on", "say", "",]
nltk_default_tag = ['AT', 'NN', 'VB', 'JJ', 'IN', 'CD', 'END']


def marvinSentenceToWord(sentence):
    word_list = list()
    for word in sentence :
        word_list = wordpunct_tokenize(sentence.lower())
    return word_list

def ARCHIVEgetSoupInfo(soup, cur_temp):
    temp = cur_temp

    try :
        title = soup.find("meta",  property="og:title")
        temp["title"] = title["content"]
    except :
        a = 0

    try :
        #print(temp["title"])
        for page_name in soup.find_all("title") :
            result = page_name.getText()
            #print(result)
    except :
        a = 0


    try :
        url = soup.find("meta",  property="og:url")
        temp["image_url"] = img_url["content"]

    except :
        a = 0


    try :
        img_url = soup.find("meta",  property="og:url")

    except :
        a = 0

    try :
        url_description = soup.find("meta",  property="og:description")
        temp["description"] = url_description["content"]
    except :
        a = 0
    #print(title["content"] if title else "No meta title given")
    #print(url["content"] if url else "No meta url given")
    temp["keywords"] = list()

    try :
        o = urllib.parse(temp["url"])
        temp["source"] = "http://" + o.netloc
    except :
        a = 0
    return temp




def marvinSaveSoup(url_obj):
    try :
        raw_html = getUrlData(url_obj.url)
        with open("marvin/static/files/rawdata/" + str(url_obj.id) + ".html", "w") as outf:
            outf.write(str(raw_html))
            outf.close()
            url_obj.soup_saved = True
            url_obj.save()
        #print("----XXXXXXXXXXXXXXXXXXX  SAVED SOUP HERE 2382492486582568 XXXXXXXXXXXXXXXXXXXXX--------")
    except :
        print("----XXXXXXXXXXXXXXXXXXX  ERROR HERE 2382492486582568 XXXXXXXXXXXXXXXXXXXXX--------")

def constructUrlTree(soup, level, parent, tree_data):
    if soup.name is not None :
        level += 1
        pk = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        #print(level, ' - ', pk, " - ", parent, level * "   ", soup.name, len(list(soup.children)))
        temp = dict()
        temp["id"] = pk
        temp["level"] = level
        temp["parent"] = parent
        temp["tag"] = soup.name
        temp["words"] = ""
        temp["string"] = ""
        temp["type"] = "resolved"
        #temp["soup"] = soup

        if soup.string is not None :
            if len(soup.string) < 250 :
                temp["string"] = soup.string
                tree_data.append(temp)
            else :
                temp["string"] = " "
        else :
            temp["string"] = " "

        for child in list(soup.children):
            constructUrlTree(child, level, pk, tree_data)
            # if no string, keep parent as parent
        return tree_data
    else :
        return "ERROR"


def constructUrlStringTree(soup, level, parent, tree_data):
    if soup.name is not None :
        level += 1
        pk = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        #print(level, ' - ', pk, " - ", parent, level * "   ", soup.name, len(list(soup.children)))
        temp = dict()
        temp["id"] = pk
        temp["level"] = level
        temp["parent"] = parent
        temp["tag"] = soup.name
        temp["words"] = ""
        temp["string"] = ""
        temp["type"] = "resolved"
        #temp["soup"] = soup

        if soup.string is not None and len(soup.string) < 250 and temp["tag"] != "script" :
            temp["string"] = soup.string
            tree_data.append(temp)
            for child in list(soup.children):
                constructUrlStringTree(child, level, pk, tree_data)
        else :
            for child in list(soup.children):
                constructUrlStringTree(child, level, parent, tree_data)
        return tree_data
    else :
        return "ERROR"

def getSoupTag():
    url = '...'

    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')

    div = soup.find('div', {'class':'class-name'})
    ps = div.find_all('p')
    lis = div.find_all('li')

    # print(the content of all <p> tags)
    for p in ps:
        print(p.text)

    # print(the content of all <li> tags)
    for li in lis:
        print(li.text)




    head_tag = soup.head
    head_tag.contents
    head_tag.string
    head_tag.parent
    last_a_tag.next_element
    last_a_tag.previous_element
    last_a_tag.previous_element.next_element
    for element in last_a_tag.next_elements:
        print(repr(element))

    sibling_soup.b.next_sibling
    sibling_soup.c.previous_sibling
    sibling_soup.b.string
    print(sibling_soup.b.string.next_sibling)

    for child in title_tag.children:
        print(child)
    for child in head_tag.descendants:
        print(child)
    for string in soup.strings:
        print(repr(string))


    for parent in link.parents:
        if parent is None:
            print(parent)
        else:
            print(parent.name)


    soup.find_all('b')
    soup.find_all(["a", "b"])
    soup.find_all(id="link2")
    soup.find_all(id=True)
    import re
    soup.find(string=re.compile("sisters"))
    soup.find_all(href=re.compile("elsie"))
    soup.find_all(href=re.compile("elsie"), id='link1')
    #data_soup.find_all(data-foo="value")

    soup.find_all("a")
    soup("a")
    soup.title.find_all(string=True)
    soup.title(string=True)
    soup.find('title')


    a_string = soup.find(string="Lacie")
    a_string.find_parent("p")


    first_link = soup.a
    first_link.find_next_siblings("a")
    first_story_paragraph = soup.find("p", "story")
    first_story_paragraph.find_next_sibling("p")
    first_story_paragraph.find_previous_sibling("p")


    first_link = soup.a
    first_link
    # <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>

    first_link.find_all_next(string=True)
    # [u'Elsie', u',\n', u'Lacie', u' and\n', u'Tillie',
    #  u';\nand they lived at the bottom of a well.', u'\n\n', u'...', u'\n']

    first_link.find_next("p")
    # <p class="story">...</p>
