from django.shortcuts import render
from django.http import Http404
# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Professor
from RMPScraper import getRMPReviews, ProfessorSearch
from django.utils import timezone

def index(request):
    popular_list = sorted(Professor.objects.all(), key=lambda professor: professor.hitCounter, reverse=True)[:5]
    last_updated_list = sorted(Professor.objects.all(), key=lambda professor: professor.lastUpdated, reverse=True)[:5]
    context = {'last_updated_list': last_updated_list, 'popular_list': popular_list}
    return render(request, "reviewer/index.html", context)

def professor(request, id):
    try:
        professor = Professor.objects.get(id=id)
        professor.hitCounter = professor.hitCounter + 1
        professor.lastUpdated = timezone.now()
        professor.save()
    except Professor.DoesNotExist:
        raise Http404("Professor does not exist.")
    return render(request, 'reviewer/professor.html', {'professor': professor})

def results(request, name):
    # TODO also get results from peoplefinder gmu
    professors = ProfessorSearch(name)
    for professor in professors:
        last_first = professor[0]
        spliced = last_first.split(",")
        first_last = ""
        for i in range(len(spliced)):
            first_last = first_last.strip() + " " + spliced[len(spliced) - 1 - i]
        try:
            professor.append(Professor.objects.get(name__contains=first_last[0:len(first_last) - 1]))
        except:
            print(len(first_last))
            print(len(professor[1]))
            new_professor = Professor(name=first_last, school=professor[1], lastUpdated=timezone.datetime(2011, 1, 1), hitCounter=0)
            new_professor.save()
            professor.append(new_professor)
    return render(request, 'reviewer/results.html', {'professors': professors})