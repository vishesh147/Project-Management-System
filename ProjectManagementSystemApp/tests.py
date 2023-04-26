from django.test import TestCase
from .models import *

# Create your tests here.

class EmployeeTestCase(TestCase):
    def setUp(self):
        elon = Employee.objects.create(employeeID='001', name='Elon Musk', email='elon@musk.com', salary=100000, role='PM')
        tim = Employee.objects.create(employeeID='002', name='Tim Cook', email='tim@cook.com', salary=90000, role='E')
        anil = Employee.objects.create(employeeID='003', name='Anil Ambani', email='anil@ambani.com', salary=70000, role='RM')

    def testEmployeeBonus(self):
        elon = Employee.objects.get(employeeID='001')
        tim = Employee.objects.get(employeeID='002')
        anil = Employee.objects.get(employeeID='003')
        self.assertEqual(elon.getBonus(), 15000)
        self.assertEqual(tim.getBonus(), 9000)
        self.assertEqual(anil.getBonus(), 7000)