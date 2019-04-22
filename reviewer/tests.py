from django.test import TestCase
from .models import Professor
from django.utils import timezone

# Create your tests here.
class dopplegangerTests(TestCase):
    def getsdopplegangerTests(self):
        professor1 = Professor(name="Michael Read", school="UVA", department="Computer Science", lastUpdated=timezone.now(), hitCounter=1)
        professor1.save()
        professor2 = Professor(name="Michael Read", school="UVA", department="Computer Science", lastUpdated=timezone.now(), hitCounter=1)
        professor2.save()
        self.assertTrue(professor2 in professor1.getDopplegangers())
       
