from django.db import models

# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    def __str__(self):
        return self.name

class Review(models.Model):
    text = models.TextField
    rating = models.TextField

class RateMyProfSnapshot(models.Model):
    url = models.URLField()
    professor_name = models.CharField(max_length=50)
    reviews = models.ManyToManyField(Review)

class Professor(models.Model):
    name = models.CharField(max_length=50)
    courses = models.ManyToManyField(Course)
    school = models.CharField(max_length=100)
    ratingPages = models.ManyToManyField(RateMyProfSnapshot)
    lastUpdated = models.DateTimeField()
    hitCounter = models.IntegerField()
    def __str__(self):
        return self.name

class redditSnapshot(models.Model):
    url = models.URLField()
    Reviews = models.ManyToManyField(Review)


    
