import requests
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

def write_to_cache(url, req_text):
    CACHE_DICTION[url] = req_text
    dumped_json_cache = json.dumps(CACHE_DICTION)
    fw = open(CACHE_FNAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

def is_covid(article_text):
    #input: text from a wh statement
    #checks if it contains covid
    #returns true or false
    covid_keywords = ['corona', 'covid', 'pandemic', 'virus', 'ppe', 'ventilator', 'antibod', 'wuhan']
    res = [kw for kw in covid_keywords if( kw in article_text.lower())]
    if len(res) >0:
        return True
    else:
        return False

def date_convert(time_string):
    time_separated = time_string.split(" ")
    art_month = time_separated[0]
    art_month = art_month[:3]
    art_month = str(datetime.datetime.strptime(art_month, "%b").month)
    if len(art_month)==1:
        art_month = "0" + art_month
    art_day = time_separated[1].replace(",", "")
    if len(art_day)==1:
        art_day = "0" + art_day
    art_year = time_separated[2]
    art_date = art_year +"-"+ art_month + "-" + art_day
    return art_date

def check_date(time_string):
    #input:a time string from the time element of an article
    #tests to see if it's in the right time frame
    # example_time_string = "Apr 3, 2020"
    art_date = date_convert(time_string)
    print(art_date)
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
    reached_time = False
    if url in CACHE_DICTION:
        print("Getting data from Cache...")
        wh_resp = CACHE_DICTION[url]
    else:
        wh_resp = requests.get(url).text
        write_to_cache(url, wh_resp)
    soup = BeautifulSoup(wh_resp, 'html.parser')
    articles = soup.find_all('article', class_='briefing-statement briefing-statement--results')
    list_of_links = []
    for article in articles:
        art_date = article.find('time').text
        if check_date(art_date)==False:
            reached_time = True
            break
        print(article.find('a')['href'])
        list_of_links.append(article.find('a')['href'])
    # turn text into soup
    #get article elements from soup
    #iterates through article elements, compiles their urls
        #run check_date on each one, stop if date is jan 19 or before and sets reached_time to True
    #returns list of article links and reached_time
    return dict(list_of_links = list_of_links, reached_time = reached_time)

def page_through_wh_statements():
    #input: baseurl? or nothing
    #iterates through pages, accumulating lists of articles
    base_url = "https://www.whitehouse.gov/briefings-statements/"
    page_url = base_url + "page/{}/"
    counter = 0
    reached_time = False
    all_article_links = []
    while True:
        counter += 1
        if counter < 2:
            article_links_response = get_article_links(base_url)
            article_links = article_links_response['list_of_links']
            reached_time = article_links_response['reached_time']
            if reached_time == True:
                break
        elif counter > 50:
            break
        else:
            article_links_response = get_article_links(page_url.format(str(counter)))
            article_links = article_links_response['list_of_links']
            reached_time = article_links_response['reached_time']
            if reached_time == True:
                break
        all_article_links.extend(article_links)
    print(len(all_article_links))
    return all_article_links

def scrape_remarks(url):
    #input: individual url for a wh statement page
    #scrapes the body text from the page/returns cached response
    #returns: dictionary with text of the statement and the date
    if url in CACHE_DICTION:
        print("Getting data from Cache...")
        wh_resp = CACHE_DICTION[url]
    else:
        wh_resp = requests.get(url).text
        write_to_cache(url, wh_resp)
    soup = BeautifulSoup(wh_resp, 'html.parser')
    title = soup.find('h1', class_="page-header__title").text
    art_date = soup.find('time').text
    art_date = date_convert(soup.find('time').text)
    print(art_date)
    content_div = soup.find('div', class_='page-content__content editor')
    for aside in content_div.find_all('aside'):
        aside.decompose()
    text_compiled = title + "\n" +content_div.text
    # all_ps = content_div.find_all('p')
    # text_compiled = ''
    # for p in all_ps:
    #     # print(p.text)
    #     text_compiled += "\n" + p.text
    # print(text_compiled)
    remarks_dict = dict(text = text_compiled, title=title, art_date=art_date)
    return remarks_dict


def remarks_to_txt(article_dict, counter):
    #input: dictionary specifying
    #saves text of the article as a txt file in a certain folder
    counter = str(counter)
    if len(counter) == 1:
        counter = "00" + counter
    elif len(counter) == 2:
        counter = "0" + counter
    file_name = 'covid_remarks/' + article_dict['art_date'] + "-" + counter + ".txt"
    file_text = [article_dict['art_date']+"\n", article_dict['text']]
    with open(file_name, "w", encoding='utf8') as outfile:
        outfile.writelines(file_text)
    return file_name

def crawl_wh_statements(list_of_article_links):
    #input: list of links to statement articles (the actual text we're going to convert)
    counter = 0
    date_to_store = ""
    for url in list_of_article_links:
        remark_dict = scrape_remarks(url)
    #run is covid to check if it's covid, if so, run remarks_to_txt to save as a txt file with the date and title as the file name
        if is_covid(remark_dict['text']):
            if remark_dict['art_date'] != date_to_store:
                counter = 0
                date_to_store = remark_dict
            counter += 1
            remarks_to_txt(remark_dict, counter)

if __name__ == '__main__':
    list_of_article_links = page_through_wh_statements()
    crawl_wh_statements(list_of_article_links)
    pass
