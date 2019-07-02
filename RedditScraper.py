import urllib.request
from bs4 import BeautifulSoup
import datetime
import json
import requests
# search for a subreddit using a name, typically this would be used to find the school
def SubredditSearch(query):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    query = str(query).replace(" ", "+")
    url = "https://www.reddit.com/subreddits/search?q=" + query
    document = requests.get(url, headers=headers)
    soup = BeautifulSoup(document.text, "html.parser")
    results = soup.findAll(name="a", attrs={"title"}, limit=2)
    link = None
    if len(results) == 2:
        link = results[1].attrs["href"]
    return link if link is not None else ""

def GetThread(url, query):
    if url == "":
        return []
    full_path = url + "search.json?q=" + query + "&restrict_sr=true"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    json1 = requests.get(full_path, headers=headers)
    json2 = json.loads(json1.text)
    posts = json2['data']['children']
    selftexts = []
    for result in posts:
        selftext = result['data']['selftext']
        date = result['data']['created']
        ups = result['data']['ups']
        permalink = result['data']['permalink']
        selftexts.append([selftext, date, ups, permalink])
    return selftexts

GetThread("https://www.reddit.com/r/gmu/","Nordstrom")
