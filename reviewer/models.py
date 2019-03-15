from django.db import models
import datetime
from django.utils import timezone
# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    def __str__(self):
        return self.name

class Review(models.Model):
    text = models.CharField(max_length=500)

class RateMyProfSnapshot(models.Model):
    url = models.URLField()
    professor_name = models.CharField(max_length=50)
    reviews = models.ManyToManyField(Review)

class Professor(models.Model):
    name = models.CharField(max_length=50)
    courses = models.ManyToManyField(Course)
    school = models.CharField(max_length=100)
    rmpLink = models.CharField(max_length=50)
    ratingPages = models.ManyToManyField(RateMyProfSnapshot)
    lastUpdated = models.DateTimeField()
    hitCounter = models.IntegerField()
    def needsUpdated(self): # hasn't been updated in 24 hours
        return not self.lastUpdated >= timezone.now() - datetime.timedelta(days=1)
    def __str__(self):
        return self.name

class redditSnapshot(models.Model):
    url = models.URLField()
    Reviews = models.ManyToManyField(Review)


    
