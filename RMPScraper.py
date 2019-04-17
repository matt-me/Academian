from bs4 import BeautifulSoup
import urllib.request
import datetime
def ProfessorSearch(prof_name):
    prof_name = prof_name.replace("_", "+")
    #print(prof_name)
    site = "http://www.ratemyprofessors.com/search.jsp?query=" + prof_name
    document = urllib.request.urlopen(site).read()
    soup = BeautifulSoup(document, "html.parser")
    results = soup.findAll(name="li", attrs={"listing PROFESSOR"})
    #print("Found " + str(len(results)) + " results.")
    professors = []
    for result in results:
        # get all of the results on the first page
        page_link = BeautifulSoup(str(result), "html.parser").a
        name = BeautifulSoup(str(page_link), "html.parser").findAll(name="span", attrs={"main"})[0].getText()
        school_subject = BeautifulSoup(str(page_link), "html.parser").findAll(name="span", attrs={"sub"})[0].getText()
        school = school_subject.split(",")[0]
        subject = school_subject.split(",")[1]
        professors.append([name, school, page_link["href"], subject])
    return professors

def SchoolSearch(prof_name):
    prof_name = prof_name.replace("_", "+")
    site = "http://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=schoolName&query=" + prof_name
    document = urllib.request.urlopen(site).read()
    soup = BeautifulSoup(document, "html.parser")
    results = soup.findAll(name="li", attrs={"listing SCHOOL"})
    schools = []
    for result in results:
        # get all of the results on the first page
        page_link = BeautifulSoup(str(result), "html.parser").a
        name = BeautifulSoup(str(page_link), "html.parser").findAll(name="span", attrs={"main"})[0].getText()
        location = BeautifulSoup(str(page_link), "html.parser").findAll(name="span", attrs={"sub"})[0].getText()
        schools.append([name, location, page_link["href"]])
    return schools

#Given a link to a RMP webpage, extract the reviews from it
def getRMPReviews(link):
    result = []
    try:
        document = urllib.request.urlopen(link).read()
    except:
        return []
    soup = BeautifulSoup(document, "html.parser")
    reviews = soup.findAll(name="tr")
    #print(len(reviews))
    for review in reviews:
        string_review = str(review)
        rating_blob = BeautifulSoup(string_review, "html.parser").find(name="td", attrs={"rating"})
        comment = BeautifulSoup(string_review, "html.parser").find(name="p", attrs={"commentsParagraph"})
        try:
            date = None
            rating = None
            formatted_line = rating_blob.getText().strip().split()
            for line in formatted_line:
                if len(line) > 2:
                    string_date = str(line).split("/")
                    if len(string_date) is 3: # if the line can be formatted into a date
                        date = datetime.date(int(string_date[2]), int(string_date[0]), int(string_date[1]))
                elif line != "Level of Difficulty" and line != "Overall Quality" and not any(c.isdigit() for c in "hello wordl"):
                    rating = line
            result.append([comment.getText().strip(), date, rating])
        except:
            pass
    return result

print(getRMPReviews("http://www.ratemyprofessors.com/ShowRatings.jsp?tid=735533"))