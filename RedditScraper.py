import urllib.request
from bs4 import BeautifulSoup
import datetime
import json
# search for a subreddit using a name, typically this would be used to find the school
def SubredditSearch(query):
    query = str(query).replace(" ", "+")
    url = "https://www.reddit.com/subreddits/search?q=" + query
    document = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(document, "html.parser")
    results = soup.findAll(name="a", attrs={"title"}, limit=1)
    link = None
    if len(results) == 1:
        link = results[0].attrs["href"]
    return link

def GetThread(url):
    json1 = urllib.request.urlopen(url).read()
    json2 = json.loads(json1)
    pass
GetThread("https://www.reddit.com/r/gmu/search.json?q=David+Nordstrom&restrict_sr=true")