from django.test import TestCase
from .models import Professor, School
from django.utils import timezone

# Create your tests here.
class dopplegangerTests(TestCase):
    def testgetsdopplegangerTests(self):
        school1 = School(name="UVA")
        school1.save()
        professor1 = Professor(name="Michael Read", school=school1, department="Computer Science", last_updated=timezone.now(), hit_counter=1)
        professor1.save()
        professor2 = Professor(name="Michael Read", school=school1, department="Computer Science", last_updated=timezone.now(), hit_counter=1)
        professor2.save()
        self.assertTrue(professor2 in professor1.getDopplegangers())
       
