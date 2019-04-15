from django.shortcuts import render
from django.http import Http404
# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Professor, ReviewSnapshot, Review, Session
from RMPScraper import getRMPReviews, ProfessorSearch
from django.utils import timezone

def index(request):
    # lists of the top 5 recent and popular professors
    popular_professors = sorted(Professor.objects.all(), key=lambda professor: professor.hitCounter, reverse=True)[:5]
    recent_professors = sorted(Professor.objects.all(), key=lambda professor: professor.lastUpdated, reverse=True)[:5]
    # the following variables are numbers 
    total_professors = len(Professor.objects.all())
    total_reviews = len(Review.objects.all())

    session_obj = None
    try:
        session_id = request.COOKIES["session_id"] # this might have a dictionary error if the user doesn't have a session id yet
        # it gets the cookie named "session_id"
        session_obj = Session.objects.get(id=session_id)
        prof_history = session_obj.history.all()
    except:
        prof_history = None
    # no need to create a new session until the user actually goes to a professor page
    context = {'prof_history': prof_history, 'recent_professors': recent_professors, 'popular_professors': popular_professors, 'total_professors': total_professors, 'total_reviews': total_reviews}
    return render(request, "reviewer/index.html", context)

def professor(request, id):
    session_obj = None
    try:
        professor = Professor.objects.get(id=id)
        professor.hitCounter = professor.hitCounter + 1
        if professor.needsUpdated():
            text_reviews = getRMPReviews("http://www.ratemyprofessors.com" + professor.rmpLink)
            snapshot = ReviewSnapshot(rmp_url=professor.rmpLink)
            snapshot.save()
            professor.ratingPages.add(snapshot)
            for review in text_reviews:
                database_review = Review(date=review[1], source="ratemyprofessor")
                database_review.setText(review[0])
                #check for a duplicate review (if two reviews have identical text fields)
                should_save = True
                for ratingPage in professor.ratingPages.all():
                    for other_review in ratingPage.reviews.all():
                        if database_review.text_hash == other_review.text_hash:
                            # don't save, because this is a duplicate review
                            should_save = False
                            print("duplicate review detected")
                if should_save: # if this is not a duplicate review
                    database_review.save()
                    snapshot.reviews.add(database_review)
        professor.lastUpdated = timezone.now()
        #professor.removeDuplicateReviews()
        professor.save()
    except Professor.DoesNotExist:
        # the professor should exist, as the only way to view a professor page is to use the search function
        # which generates professor pages on search results
        raise Http404("Professor does not exist.")
   
    try:
        session_id = request.COOKIES["session_id"]
        # See if the user has a valid session
        session_obj = Session.objects.get(id=session_id)
    except (TypeError, KeyError, ValueError) as e:
        # else create a new session
        session_obj = Session()
        session_obj.save()
        session_id = session_obj.id
        print(session_obj.id)
    session_obj.history.add(Professor.objects.get(id=id))
    session_obj.save()
    response = render(request, 'reviewer/professor.html', {'prof_history': session_obj.history.all(), 'professor': professor})
    response.set_cookie("session_id", session_id)
    return response

def results(request, name):
    professors = ProfessorSearch(name)
    for professor in professors:
        last_first = professor[0]
        spliced = last_first.split(",")
        first_last = ""
        for i in range(len(spliced)):
            first_last = first_last.strip() + " " + spliced[len(spliced) - 1 - i]
        try:
            print("Searching for: " + first_last[0:len(first_last)])
            print("Contains: " + professor[1])
            prof_object = Professor.objects.get(name__contains=first_last[0:len(first_last)], school__contains=professor[1])
            professor.append(prof_object)
        except Professor.DoesNotExist:
            new_professor = Professor(name=first_last, school=professor[1], lastUpdated=timezone.datetime(2011, 1, 1), hitCounter=0, rmpLink=professor[2])
            new_professor.save()
            professor.append(new_professor)
    return render(request, 'reviewer/results.html', {'professors': professors})
    