from django.shortcuts import render
from django.http import Http404
# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Professor, RateMyProfSnapshot, Review
from RMPScraper import getRMPReviews, ProfessorSearch
from django.utils import timezone

def index(request):
    popular_list = sorted(Professor.objects.all(), key=lambda professor: professor.hitCounter, reverse=True)[:5]
    last_updated_list = sorted(Professor.objects.all(), key=lambda professor: professor.lastUpdated, reverse=True)[:5]
    total_professors = len(Professor.objects.all())
    total_reviews = len(Review.objects.all())
    context = {'last_updated_list': last_updated_list, 'popular_list': popular_list, 'total_professors': total_professors, 'total_reviews': total_reviews}
    return render(request, "reviewer/index.html", context)

def professor(request, id):
    try:
        professor = Professor.objects.get(id=id)
        professor.hitCounter = professor.hitCounter + 1
        if professor.needsUpdated():
            #print("http://www.ratemyprofessors.com" + professor.rmpLink)
            text_reviews = getRMPReviews("http://www.ratemyprofessors.com" + professor.rmpLink)
            snapshot = RateMyProfSnapshot(url=professor.rmpLink)
            snapshot.save()
            professor.ratingPages.add(snapshot)
            for review in text_reviews:
                database_review = Review(text=review)
                database_review.save()
                snapshot.reviews.add(database_review)
        professor.lastUpdated = timezone.now()
        professor.save()
    except Professor.DoesNotExist:
        raise Http404("Professor does not exist.")
    return render(request, 'reviewer/professor.html', {'professor': professor})

def results(request, name):
    professors = ProfessorSearch(name)
    for professor in professors:
        last_first = professor[0]
        spliced = last_first.split(",")
        first_last = ""
        for i in range(len(spliced)):
            first_last = first_last.strip() + " " + spliced[len(spliced) - 1 - i]
        try:
            prof_object = Professor.objects.get(name__contains=first_last[0:len(first_last) - 1]).objects.get(school__contains=professor[1])
            professor.append(prof_object)
        except:
            #print(len(first_last))
            #print(len(professor[1]))
            # professor doesn't exist
            # add a new professor to the database
            new_professor = Professor(name=first_last, school=professor[1], lastUpdated=timezone.datetime(2011, 1, 1), hitCounter=0, rmpLink=professor[2])
            new_professor.save()
            professor.append(new_professor)
    return render(request, 'reviewer/results.html', {'professors': professors})
    