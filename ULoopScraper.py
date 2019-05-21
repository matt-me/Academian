import urllib.request
from bs4 import BeautifulSoup
import datetime

# returns a list of professors matching prof_name
def ULoopSearch(prof_name):
    prof_name = prof_name.replace("_", "+")
    url = "http://www.uloop.com/professors/?s=" + prof_name
    document = urllib.request.urlopen(url).read() # open the webpage for reading
    soup = BeautifulSoup(document, "html.parser")
    professors = []
    results = soup.findAll(name="div", attrs={"professor_item", "list-row-clickable"})
    for result in results:
        result_box = BeautifulSoup(str(result), "html.parser").div
        name = result_box.contents[1].getText().strip()
        department = result_box.contents[5].getText().strip()
        page_link = result_box.contents[1].a.attrs["href"]
        professors.append([name, None, page_link, department])
        # The school doesn't show up on the search
    return professors

# returns a list of reviews from the uloop link and star ratings
def GetULoopReviews(link):
    full_link = "http://www.uloop.com/" + link
    document = urllib.request.urlopen(full_link).read() # open the webpage for reading
    soup = BeautifulSoup(document, "html.parser")
    comments_html = soup.findAll(name="span", attrs={"comment"})
    ratings_html = soup.findAll(name="td")
    school_html = soup.findAll(name="table", attrs={"professor_detail"})
    school_soup = BeautifulSoup(str(school_html), "html.parser")
    school = school_soup.find("a").getText() # get the school name, because uloop doesn't update it on the search page
    comments = []
    ratings = []
    for comment in comments_html:
        comments.append(comment.getText().strip())
    for rating_html in ratings_html:
        rating_stars_html = BeautifulSoup(str(rating_html), "html.parser")
        rating_stars = rating_stars_html.findAll(name="img", attrs="rate_star")
        if len(rating_stars) == 20:
            for i in range(0, 4):
                star_count = list(map(lambda x: x.attrs['src'].count("https://www.uloop.com/img/star-full.png"), list(rating_stars[i*5: i*5+5]))).count(1)
                ratings.append(star_count)
    return [comments, ratings, school]
    
    # NOTE: ULoop reviews basically have no date associated with them on the website, so they will have to just be inserted as something more abstract
    # perhaps a separate category?