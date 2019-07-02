import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import Http404
# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Professor, ReviewSnapshot, Review, Session, School
from RMPScraper import getRMPReviews, ProfessorSearch
from ULoopScraper import ULoopSearch, GetULoopReviews
from RedditScraper import *
from django.utils import timezone
from .forms import ReviewForm

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
    professor_obj = None
    try:
        uloop_reviews = [[]]
        professor_obj = Professor.objects.get(id=id)
        professor_obj.hit_counter = professor_obj.hit_counter + 1
        if True:#professor_obj.needsUpdated():
            rmp_reviews = getRMPReviews("http://www.ratemyprofessors.com" + professor_obj.rmp_link)
            reddit_posts = GetThread(professor_obj.school.subreddit, professor_obj.name)
            #reddit_posts = GetThread()
            # if the professor has a uloop page
            if (professor_obj.uloop_link != ""):
                # GetULoopReviews also returns the school from the page at uloop_reviews[2]
                uloop_reviews = GetULoopReviews(professor_obj.uloop_link)
                if (uloop_reviews[2] != professor_obj.school.name):
                    # if this is true, then it means that the wrong uloop link got assigned. it must be set to "" and tried again
                    # this is expected to happen in some cases, so let's handle it
                    uloop_reviews[0] = []
                    try:
                        actual_professor = Professor.objects.get(name=professor_obj.name, department=professor_obj.department, school__name=uloop_reviews[2])
                        actual_professor.uloop_link = professor_obj.uloop_link
                        actual_professor.save()
                    except Professor.DoesNotExist:
                        pass # the professor for the right school doesn't exist yet, which is fine and simply means that nothing needs to be done
                    professor_obj.uloop_link = ""
                if professor_obj.school.name == "":
                    professor_obj.setSchool(uloop_reviews[2])
            rmp_snapshot = ReviewSnapshot(url=professor_obj.rmp_link)
            rmp_snapshot.save()
            uloop_snapshot = ReviewSnapshot(url=professor_obj.uloop_link)
            uloop_snapshot.save()
            reddit_snapshot = ReviewSnapshot(url="reddit.com") 
            reddit_snapshot.save()
            professor_obj.rating_pages.add(rmp_snapshot)
            professor_obj.rating_pages.add(uloop_snapshot)
            professor_obj.rating_pages.add(reddit_snapshot)
            # Get rmp_reviews
            for review in rmp_reviews:
                database_review = Review(date=review[1], source="ratemyprofessor", rating=review[2])
                database_review.setText(review[0])
                #check for a duplicate review (if two reviews have identical text fields)
                should_save = True
                for rating_page in professor_obj.rating_pages.all():
                    for other_review in rating_page.reviews.all():
                        if database_review.text_hash == other_review.text_hash:
                            # don't save, because this is a duplicate review
                            should_save = False
                if should_save: # if this is not a duplicate review
                    database_review.save()
                    rmp_snapshot.reviews.add(database_review)
            #Get uLoop reviews
            for review in uloop_reviews[0]:
                if (len(review) == 0):
                    break
                database_review = Review(date=timezone.datetime(2011, 1, 1), source="uLoop")
                database_review.setText(str(review))
                should_save = True
                for rating_page in professor_obj.rating_pages.all():
                    for other_review in rating_page.reviews.all():
                        if database_review.text_hash == other_review.text_hash:
                            # don't save, because this is a duplicate review
                            should_save = False
                if should_save: # if this is not a duplicate review
                    database_review.save()
                    uloop_snapshot.reviews.add(database_review)
                    # since this is uloop, it's possible the school wasn't cached during the search (if it didn't exist on RMP)
            for post in reddit_posts:
                if (post[0] != ""):
                    database_review = Review(date=datetime.datetime.fromtimestamp(post[1]), source="reddit")
                    database_review.setText(post[0])
                    should_save = True
                    for rating_page in professor_obj.rating_pages.all():
                        for other_review in rating_page.reviews.all():
                            if database_review.text_hash == other_review.text_hash:
                                # don't save, because this is a duplicate review
                                should_save = False
                    if should_save: # if this is not a duplicate review
                        database_review.save()
                        reddit_snapshot.reviews.add(database_review)
        professor_obj.last_updated = timezone.now()
        #professor.removeDuplicateReviews()
        professor_obj.save()
    except Professor.DoesNotExist:
        # the professor should exist, as the only way to view a professor page is to use the search function
        # which generates professor pages on search results
        raise Http404("Professor does not exist.")
    # now upkeep the session history
    try:
        session_id = request.COOKIES["session_id"]
        # See if the user has a valid session
        session_obj = Session.objects.get(id=session_id)
    except (TypeError, KeyError, ValueError, Session.DoesNotExist) as e:
        # else create a new session
        session_obj = Session()
        session_id = session_obj.id
        session_obj.save()
    session_obj.history.add(Professor.objects.get(id=id))
    session_obj.save()
    # the following code is for the submission form
    if request.method == 'POST':
        # create a new review
        new_review = Review(source="admin", date=timezone.now())
        new_review.setText(request.POST['text'])
        new_review.save()
        professor_obj.user_reviews.add(new_review)
        professor_obj.save()
        # create a form instance and populate it with data from the request:
        form = ReviewForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            # return HttpResponseRedirect('/thanks/')
            pass
    else:
        form = ReviewForm()
        pass

    # submit the response to view the professor page
    response = render(request, 'reviewer/professor.html', {'prof_history': session_obj.history.all(), 'professor': professor_obj, 'dopplegangers': professor_obj.getDopplegangers(), "alternate_identities": professor_obj.getAlternateIdentities(), 'form': form})
    response.set_cookie("session_id", session_id)
    return response

def results(request, name):
    rmp_professors = ProfessorSearch(name) # [name, school, page_link["href"], subject]
    uloop_professors = ULoopSearch(name)
    professor_list = []
    new_professor = None
    # First get the professors from RateMyProfessor
    for professor_obj in rmp_professors:
        # first format the name
        last_first = professor_obj[0]
        spliced = last_first.split(",")
        first_last = ""
        for i in range(len(spliced)):
            first_last = first_last.strip() + " " + spliced[len(spliced) - 1 - i]
        try:
            database_object = Professor.objects.get(name=first_last[0:len(first_last)], school__name=professor_obj[1], department=professor_obj[3])
            if (database_object.department != professor_obj[3]):
                # set the department to what it is
                database_object.department = professor_obj[3]
            professor_list.append(database_object)
            database_object.save()
            new_professor = database_object
        except Professor.DoesNotExist:
            new_professor = Professor(name=first_last, department=professor_obj[3], last_updated=timezone.datetime(2011, 1, 1), hit_counter=0, rmp_link=professor_obj[2], uloop_link="")
            new_professor.setSchool(professor_obj[1])
            new_professor.save()
            professor_list.append(new_professor)
        if new_professor.school.name != "" and (new_professor.school.subreddit is None or new_professor.school.subreddit == ""):
                # need to find the subreddit for the school
                subreddit = SubredditSearch(new_professor.school.name)
                new_professor.school.subreddit = subreddit
                new_professor.school.save()
    formatted_list = sorted(professor_list, key=lambda professor: professor.hit_counter)
    #sorted returns it in the opposite order
    formatted_list.reverse()
    # Now get the uLoop professors
    for professor_obj in uloop_professors:
        try:
            database_object = Professor.objects.get(name=professor_obj[0], department=professor_obj[3])
            # one professor found in the database
            if database_object not in formatted_list:
                # if it wasn't in ratemyprofessor, then it should be added to the list
                formatted_list.append(database_object)
            if database_object.uloop_link == "":
                # if it was, then it should be given a uloop link if it doesn't have one already - it might be new
                database_object.uloop_link = professor_obj[2]
                database_object.save()
        except Professor.DoesNotExist:
            # new professor is not in the database yet, and not in ratemyprofessor
            new_professor = Professor(name=professor_obj[0], department=professor_obj[3], last_updated=timezone.datetime(2011, 1, 1), hit_counter=0, uloop_link=professor_obj[2])
            # will have to update the school field later, for now set it to a null default
            # this is because uloop does not provide the school name when doing a search
            new_professor.setSchool("")
            new_professor.save()
            formatted_list.append(new_professor)
            if new_professor.school.name != "" and (new_professor.school.subreddit is not None or new_professor.school.subreddit == ""):
                # need to find the subreddit for the school
                subreddit = SubredditSearch(new_professor.school.name)
                new_professor.school.subreddit = subreddit
                new_professor.school.save()
        except Professor.MultipleObjectsReturned:
            # professor teaches at more than one university
            # this is problematic because uloop does not differentiate between schools on the search page
            database_objects = Professor.objects.filter(name=professor_obj[0], department=professor_obj[3])
            for guy in database_objects:
                if (guy.uloop_link == ""):
                    guy.uloop_link = professor_obj[2]
                    guy.save()
                    # searched professor has the same name and the same department as the one in the database, but we aren't sure if it has the same school
                    # so, just assign it to any uloop link. If this turns out to be wrong, it can always be changed before the professor page is displayed
                if guy not in formatted_list:
                    formatted_list.append(guy)
    return render(request, 'reviewer/results.html', {'professors': formatted_list, "professor_count": len(formatted_list)})

def about(request):
    return render(request, 'reviewer/about.html')

