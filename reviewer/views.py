from django.shortcuts import render
from django.http import Http404
# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Professor
from RMPScraper import getRMPReviews, ProfessorSearch

def index(request):
    last_updated_list = sorted(Professor.objects.all(), key=lambda professor: professor.hitCounter)
    popular_list = sorted(Professor.objects.all(), key=lambda professor: professor.hitCounter)
    context = {'last_updated_list': last_updated_list, 'popular_list': popular_list}
    return render(request, "reviewer/index.html", context)

def professor(request, id):
    try:
        professor = Professor.objects.get(id=id)
        professor.hitCounter = professor.hitCounter + 1
    except Professor.DoesNotExist:
        raise Http404("Professor does not exist. Will scrape for it soon.")
    return render(request, 'reviewer/professor.html', {'professor': professor})

def results(request, name):
    try:
        professors = ProfessorSearch(name)
    except:
        pass
    return render(request, 'reviewer/results.html', {'professors': professors})