from django.urls import path

from . import views

urlpatterns = [
    path('professor/<slug:id>/', views.professor, name='professor'),
    path('search/<slug:name>/', views.results, name='professor'),
    path('', views.index, name='index')
]