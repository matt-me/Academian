from django.db import models
import datetime
import pytz
from django.utils import timezone
import hashlib
# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    school = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Review(models.Model):
    text = models.CharField(max_length=500)
    date = models.DateField()
    source = models.CharField(max_length=20)
    text_hash = models.CharField(max_length=53)

    def isNew(self):
        return pytz.utc.localize(datetime.datetime.combine(self.date, datetime.time(0, 0, 0))) >= timezone.now() - datetime.timedelta(days=60)
    
    def getDateString(self): # returns which semester the review was written during (e.g Spring 2018)
        if (self.date.month >= 1 and self.date.month <= 5): # Spring semester
            return "Spring " + str(self.date.year)
        if (self.date.month >= 6 and self.date.month <= 8): # Summer semester
            return "Summer " + str(self.date.year)
        else:
            return "Fall " + str(self.date.year)

    def setText(self, text):
        self.text = text
        m = hashlib.md5()
        m.update(text.encode('utf-8'))
        m.digest()
        self.text_hash = m.hexdigest()

    def __eq__(self, other): # Check if two reviews are equal. This will remove duplicate reviews that come from the same website
        return other.text_hash and other.source and self.text_hash == other.text_hash and self.source == other.source

class ReviewSnapshot(models.Model):
    rmp_url = models.URLField()
    professor_name = models.CharField(max_length=50)
    reviews = models.ManyToManyField(Review)

class Professor(models.Model):
    name = models.CharField(max_length=50)
    courses = models.ManyToManyField(Course)
    school = models.CharField(max_length=100)
    rmpLink = models.CharField(max_length=50)
    ratingPages = models.ManyToManyField(ReviewSnapshot)
    lastUpdated = models.DateTimeField()
    hitCounter = models.IntegerField()

    def needsUpdated(self): # hasn't been updated in 24 hours
        return not self.lastUpdated >= timezone.now() - datetime.timedelta(days=1)
    
    def hasNew(self):
        for ratingPage in self.ratingPages.all():
            for review in ratingPage.reviews.all():
                return pytz.utc.localize(datetime.datetime.combine(review.date, datetime.time(0, 0, 0))) >= timezone.now() - datetime.timedelta(days=60)
    
    def reviewCount(self):
        i = 0
        for ratingPage in self.ratingPages.all():
            for review in ratingPage.reviews.all():
                i += 1
        return i
    def removeDuplicateReviews(self):
        for ratingPage in self.ratingPages.all():
            for review in ratingPage.reviews.all():
                for otherRatingPage in self.ratingPages.all():
                    for otherReview in ratingPage.reviews.all():
                        if review.text_hash == otherReview.text_hash and review.id != otherReview.id:
                            otherReview.delete()
                            print("removing duplicate review")
    def __str__(self):
        return self.name

#This will keep track of the professors that the user has recently viewed
class Session(models.Model):
    history = models.ManyToManyField(Professor)

class redditSnapshot(models.Model):
    url = models.URLField()
    reviews = models.ManyToManyField(Review)
