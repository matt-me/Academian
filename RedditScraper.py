import urllib.request
from bs4 import BeautifulSoup
import datetime
document = urllib.request.urlopen(url).read()
def SubredditSearch(query):
    query = str(query).replace(" ", "+")
    url = "https://www.reddit.com/subreddits/search?q=query"