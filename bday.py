# -*- coding: utf-8 -*-

import sys
import requests
from urllib.parse import urlencode, urlparse, parse_qs
from datetime import datetime, date, time
import calendar
import time
import json

with open('config.json') as data_file:    
    data = json.load(data_file)

if not data["token"]:
    print ("Insert token")
    exit(0) 

if not data["bday"]:
    print ("Insert your birthday")
    exit(0)


# access token
access_token = data["token"] 

#your birthday
bday = datetime.strptime(data["bday"], "%Y-%m-%d")
bday_start = datetime(bday.year, bday.month, bday.day)
bday_end = datetime(bday.year, bday.month, bday.day +1)

# unix timestamp
ut_bday_start = time.mktime(bday_start.timetuple())
ut_bday_end = time.mktime(bday_end.timetuple())

#the list of language
languages = ["eng","fr","it"]

#the list of messages response by languages
messages = {"eng" : "Thanks by VitBot!", "fr": "Merci de VitBot!", "it": "Grazie da VitBot!"}

#bday words to check
bdaywords = {"eng": ["happy", "bday", "b\'day", "birthday","hbd", "wish", "returns"], "fr": ["bon", "joyeux", "anniversaire"], "it": ["compleanno", "auguri"]}

def isWish (message):
    for lang in languages:
        for word in bdaywords[lang]:
            if word.lower() in message.lower():
                return lang
    return False

def getAnsware (lang):
    return messages[lang]

#get posts
def get_posts(url, feeds=None):

    if feeds is None:
        feeds = []
    
    req = requests.get(url)
    if req.status_code == 200:
        
        content = req.json()

        if len(content['data']) == 0:
            return feeds

        #keep only relevant fields from post data
        for post in content['data']:
            feeds.append({'id': post['id'], 'message': post.get('message', ''), 'from': post['from']['name'], 'type': post['type'], 'date': post['created_time']})        
        
        next_url = content['paging']['next']
        
        return get_posts(next_url, feeds)
    else:
        print ("Unable to connect. Check if token is still valid")
        exit(0)

def wishFilter (posts_array):
    wishes = []
    #keep only posts relevant to birthday
    for post in posts_array:
        if post['type']=='status' and isWish(post['message'] ) :
            wishes.append(post)

    return wishes


if __name__ == '__main__':
    
    #get bithday wishes
    base_url = 'https://graph.facebook.com/v2.1/me/feed'
    params = {'access_token': access_token, 'fields': 'id,type,created_time,from,message', 'since': ut_bday_start, 'until': ut_bday_end}
    url = '%s?%s' % (base_url, urlencode(params))
    posts = get_posts(url)
    wishPosts = wishFilter(posts)
    #confirm before posting
    print ("Date: " + str(bday))
    print ("Posts number: " + str(len(posts)))
    print ("Wish Posts number: " + str(len(wishPosts)))
    print ("------------------------")
    print ("Posts: ")
    for post in posts:
        print (post)
    print ("------------------------")
    print ("Wish Posts: ")
    for post in wishPosts:
        print (post)