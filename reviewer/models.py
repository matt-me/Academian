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
        
class School(models.Model):
    name = models.CharField(max_length=50)
    subreddit = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    
class Review(models.Model):
    text = models.CharField(max_length=500)
    date = models.DateField()
    source = models.CharField(max_length=20)
    text_hash = models.CharField(max_length=53)
    rating = models.CharField(max_length=20)

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
    department = models.CharField(max_length=100)
    rmp_link = models.CharField(max_length=50)
    uloop_link = models.CharField(max_length=50)
    rating_pages = models.ManyToManyField(ReviewSnapshot)
    last_updated = models.DateTimeField()
    hit_counter = models.IntegerField()

    def needsUpdated(self): # hasn't been updated in 24 hours
        return not self.last_updated >= timezone.now() - datetime.timedelta(days=1)
    
    def hasNew(self):
        for rating_page in self.rating_pages.all():
            for review in rating_page.reviews.all():
                return pytz.utc.localize(datetime.datetime.combine(review.date, datetime.time(0, 0, 0))) >= timezone.now() - datetime.timedelta(days=60)
    
    def reviewCount(self):
        i = 0
        for rating_page in self.rating_pages.all():
            for review in rating_page.reviews.all():
                i += 1
        return i
    def removeDuplicateReviews(self):
        for rating_page in self.rating_pages.all():
            for review in rating_page.reviews.all():
                for other_rating_page in self.rating_pages.all():
                    for other_review in rating_page.reviews.all():
                        if review.text_hash == other_review.text_hash and review.id != other_review.id:
                            other_review.delete()
    # see if there's a professor at the same school with a similar name
    def getDopplegangers(self):
        dopplegangers = []
        professor_name_list = self.name.split(" ")
        # get all of the professors teaching at this professor's school's department 
        other_professors = Professor.objects.filter(school__contains=self.school, department__contains=self.department)
        for professor in other_professors:
            other_name_list = professor.name.split(" ")
            if (len(professor_name_list) == len(other_name_list) and professor is not self):
                # check to see if one of the professors names were shortened to an initial
                # Ex. David Nordstrom and D Nordstrom
                # TODO refactor this garbage
                for i in range(len(other_name_list)):
                    end_loop = False
                    for j in range(len(professor_name_list)):
                        if i == j and other_name_list[i][0] != professor_name_list[i][0]:
                            end_loop = True
                            break
                        elif i != j and other_name_list[j] != professor_name_list[j]:
                            end_loop = True
                            break
                    if end_loop:
                        break
                    else:
                        dopplegangers.append(professor)
        return dopplegangers
        # returns professors that teach at a different school in the same subject with the same name
    def getAlternateIdentities(self):
        alternate_identities = Professor.objects.filter(name__contains=self.name, department__contains=self.department).exclude(school__contains=self.school)

        return alternate_identities
    def __str__(self):
        return self.name

class ULoopReview(models.Model):
    overall = models.IntegerField()
    helpfulness = models.IntegerField()
    clarity = models.IntegerField()
    easiness = models.IntegerField()
    review = models.OneToOneField(Review, on_delete=models.CASCADE)

#This will keep track of the professors that the user has recently viewed
class Session(models.Model):
    history = models.ManyToManyField(Professor)

class redditSnapshot(models.Model):
    url = models.URLField()
    reviews = models.ManyToManyField(Review)
