ueimport requests
import json
from bs4 import BeautifulSoup
import datetime


CACHE_FNAME = 'wh_cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

covid_keywords = ['corona', 'covid', 'pandemic', 'virus', 'ppe', 'ventilator', 'antibod', 'wuhan']



soup = BeautifulSoup(wh_resp, 'html.parser')
address_divs = soup.find('article', class_='briefing-statement briefing-statement--results')

def write_to_cache(url, req_text):
    CACHE_DICTION[url] = req_text
    dumped_json_cache = json.dumps(CACHE_DICTION)
    fw = open(CACHE_FNAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

def check_date(time_string)):
    #input:a time string from the time element of an article
    #tests to see if it's in the right time frame
    # example_time_string = "Apr 3, 2020"
    time_separated = time_string.split(" ")
    art_month = time_separated[0]
    art_day = time_separated[1].replace(",", "")
    art_year = time_separated[2]
    art_date = year +"-"+ str(datetime.datetime.strptime(art_month, "%b").month) + "-" + art_day
    if art_date > "2020-01-19":
        return True
    else:
        print("We are in the before times")
        return False
    #returns True if date is on or after January 20th, 2020, else False
    pass

def get_article_links(url):
    #input:url page of articles from the wh briefing list
    #scrapes page, get text, pull urls from <articles>
    #check cache for url
    if url in CACHE_DICTION:
        print("Getting data from Cache...")
    else:
        wh_resp = requests.get(url).text
        write_to_cache(url, wh_resp)
    # turn text into soup
    #get article elements from soup
    #iterates through article elements, compiles their urls
        #run check_date on each one, stop if date is jan 19 or before
    #returns list of article pages
    pass

def get_covid_remarks(url):
    #input: a url of an article
    #checks if it contains covid keywords
    #if it contains any of the keywords, saves text of the article as a txt file in a certain folder
    pass

def page_through_wh_statements():
    #input: baseurl? or nothing
    #iterates
    base_url = "https://www.whitehouse.gov/briefings-statements/"
    page_url = base_url + "page/{}/"
    pass
