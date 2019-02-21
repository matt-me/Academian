from bs4 import BeautifulSoup
import urllib.request

def ProfessorSearch(prof_name):
    prof_name = prof_name.replace("_", "+")
    print(prof_name)
    site = "http://www.ratemyprofessors.com/search.jsp?query=" + prof_name
    document = urllib.request.urlopen(site).read()
    soup = BeautifulSoup(document, "html.parser")
    results = soup.findAll(name="li", attrs={"listing PROFESSOR"})
    print("Found " + str(len(results)) + " results.")
    professors = []
    for result in results:
        # get all of the results on the first page
        page_link = BeautifulSoup(str(result), "html.parser").a
        name = BeautifulSoup(str(page_link), "html.parser").findAll(name="span", attrs={"main"})[0].getText()
        school = BeautifulSoup(str(page_link), "html.parser").findAll(name="span", attrs={"sub"})[0].getText()
        print(name)
        print(school)
        print(page_link["href"])
        professors.append([name, school, page_link["href"]])
    return professors

#Given a link to a RMP webpage, extract the reviews from it
def getRMPReviews(link):
    result = []
    document = urllib.request.urlopen(link).read()
    soup = BeautifulSoup(document, "html.parser")
    reviews = soup.findAll(name="tr")
    print(len(reviews))
    for review in reviews:
        rating = BeautifulSoup(str(review), "html.parser").find(name="td", attrs={"rating"})
        comment = BeautifulSoup(str(review), "html.parser").find(name="p", attrs={"commentsParagraph"})
        try:
            print(comment.getText().strip())
            result.append(comment.getText().strip())
        except:
            pass
    return result

#getRMPReviews("http://www.ratemyprofessors.com/ShowRatings.jsp?tid=735533")