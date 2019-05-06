from django.shortcuts import render
from django.http import Http404
# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Professor, ReviewSnapshot, Review, Session
from RMPScraper import getRMPReviews, ProfessorSearch
from ULoopScraper import ULoopSearch, GetULoopReviews
from django.utils import timezone

def index(request):
    # lists of the top 5 recent and popular professors
    popular_professors = sorted(Professor.objects.all(), key=lambda professor: professor.hit_counter, reverse=True)[:5]
    recent_professors = sorted(Professor.objects.all(), key=lambda professor: professor.last_updated, reverse=True)[:5]
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
        professor.hit_counter = professor.hit_counter + 1
        if professor.needsUpdated():
            text_reviews = getRMPReviews("http://www.ratemyprofessors.com" + professor.rmp_link)
            snapshot = ReviewSnapshot(rmp_url=professor.rmp_link)
            snapshot.save()
            professor.rating_pages.add(snapshot)
            for review in text_reviews:
                database_review = Review(date=review[1], source="ratemyprofessor", rating=review[2])
                database_review.setText(review[0])
                #check for a duplicate review (if two reviews have identical text fields)
                should_save = True
                for rating_page in professor.rating_pages.all():
                    for other_review in rating_page.reviews.all():
                        if database_review.text_hash == other_review.text_hash:
                            # don't save, because this is a duplicate review
                            should_save = False
                if should_save: # if this is not a duplicate review
                    database_review.save()
                    snapshot.reviews.add(database_review)
        professor.last_updated = timezone.now()
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
    response = render(request, 'reviewer/professor.html', {'prof_history': session_obj.history.all(), 'professor': professor, 'dopplegangers': professor.getDopplegangers(), "alternate_identities": professor.getAlternateIdentities()})
    response.set_cookie("session_id", session_id)
    return response

def results(request, name):
    rmp_professors = ProfessorSearch(name)
    uloop_professors = ULoopSearch(name)
    professor_list = []
    for professor in rmp_professors:
        # first format the name
        last_first = professor[0]
        spliced = last_first.split(",")
        first_last = ""
        for i in range(len(spliced)):
            first_last = first_last.strip() + " " + spliced[len(spliced) - 1 - i]
        try:
            prof_object = Professor.objects.get(name=first_last[0:len(first_last)], school=professor[1])
            if (prof_object.department != professor[3]):
                prof_object.department = professor[3] # set the department to what it is
            professor_list.append(prof_object)
            prof_object.save()
        except Professor.DoesNotExist:
            new_professor = Professor(name=first_last, school=professor[1], department=professor[3], last_updated=timezone.datetime(2011, 1, 1), hit_counter=0, rmp_link=professor[2])
            new_professor.save()
            professor_list.append(new_professor)
    formatted_list = sorted(professor_list, key=lambda professor: professor.hit_counter)
    formatted_list.reverse() #sorted returns it in the opposite order
    for professor in uloop_professors:
        try:
            prof_object = Professor.objects.get(name=professor[0], department=professor[3])
            if prof_object not in formatted_list:
                formatted_list.append(prof_object) # exists in uloop but not ratemyprofessor, so add it to the search results
        except Professor.DoesNotExist:
            # add the professor to the list
            new_professor = Professor(name=professor[0], school="", department=professor[3], last_updated=timezone.datetime(2011, 1, 1), hit_counter=0, rmp_link=professor[2])
            new_professor.save()
            formatted_list.append(new_professor)
    return render(request, 'reviewer/results.html', {'professors': formatted_list})
    