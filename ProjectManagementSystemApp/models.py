from djongo import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from tinymce.models import HTMLField
from datetime import datetime
from django.utils import timezone
from django.db.models import Avg
from django.forms import ModelForm

# Create your models here.

class Team(models.Model):
    teamID = models.SlugField(primary_key=True, max_length=10)
    name = models.CharField(max_length=64)
    description = models.TextField(default="")
    managerID = models.CharField(max_length=10)
    managerName = models.CharField(max_length=64)
    size = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(blank=True, auto_now_add=True)

    def __str__(self):
        return self.teamID


class Task(models.Model):
    taskID = models.SlugField(primary_key=True, max_length=32)
    title = models.CharField(max_length=64)
    description = models.TextField()
    deadline = models.DateTimeField(blank=True)
    submitted = models.DateTimeField(blank=True)
    completed = models.DateTimeField(blank=True)
    assigned = models.DateTimeField()
    allocatedBudget = models.PositiveIntegerField()
    utilizedBudget = models.PositiveIntegerField(null=True, blank=True)
    report = HTMLField(blank=True)
    employeeID = models.SlugField(max_length=10)
    employeeName = models.CharField(max_length=64)
    projectID = models.SlugField(max_length=15)
    managerID = models.SlugField(max_length=10)
    teamID = models.SlugField(max_length=10)
    status = models.CharField(max_length=1, default='I',
        choices=[
            ('I', 'In Progress'),
            ('C', 'Completed'),
            ('R', 'Submitted For Review')
    ])
    rating = models.PositiveSmallIntegerField(blank=True)
 
    def __str__(self):
        return self.taskID
    
class ReportForm(ModelForm):
    class Meta:
        model = Task
        fields = ['report', 'utilizedBudget']



class Employee(models.Model):
    employeeID = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=64)
    email = models.EmailField()
    joiningDate = models.DateField(auto_now_add=True, null=True, blank=True)
    salary = models.PositiveIntegerField(default=0)
    role = models.CharField(max_length=6, default='E',
        choices=[
            ("PM", "Project Manager"),
            ("RM", "Resource Manager"),
            ("E", "Employee"),
            ("O", "Owner")
        ])
    teamID = models.CharField(null=True, blank=True, max_length=10)
    teamName = models.CharField(blank=True, max_length=64)
    managerID = models.CharField(null=True, blank=True, max_length=10)
    managerName = models.CharField(blank=True, max_length=64)
    avgRating = models.FloatField(blank=True)

    def __str__(self):
        return self.employeeID
    
    def getBonus(self):
        if self.role == 'PM':
            return (self.salary)*0.15;
        else:
            return (self.salary)*0.10;

    def updateRating(self):
        if self.role == 'E':
            tasks = Task.objects.filter(employeeID=self.employeeID).aggregate(Avg("rating"))
            self.avgRating = tasks['rating__avg']
        else:
            pass


@receiver(post_save, sender=User)
def UpdateEmployee(sender, instance=None, created=False, **kwargs):
    if instance.is_staff:
       pass 
    if created:
        Employee.objects.create(
            employeeID=instance.username,
            name=instance.get_full_name(),
            email=instance.email
        )
    else:
        try:
            employee = Employee.objects.get(employeeID=instance.username)
            employee.employeeID = instance.username
            employee.name = instance.get_full_name()
            employee.email = instance.email
            employee.save()
        except:
            Employee.objects.create(
                employeeID=instance.username,
                name=instance.get_full_name(),
                email=instance.email
            )
    


class Project(models.Model):
    projectID = models.SlugField(primary_key=True, max_length=15)
    title = models.CharField(max_length=64)
    client = models.CharField(max_length=64)
    description = models.TextField()
    allocatedBudget = models.PositiveIntegerField(blank=True)
    utilizedBudget = models.PositiveIntegerField(blank=True, default=0)
    deadline = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(blank=True)
    status = models.CharField(max_length=1, default='O',
        choices=[
            ('O', 'Ongoing'),
            ('C', 'Completed'),
    ])
    
    teamID = models.CharField(blank=True, max_length=10)
    teamName = models.CharField(blank=True, max_length=64)
    managerID = models.CharField(blank=True, max_length=10)
    managerName = models.CharField(blank=True, max_length=64)
    
    overbudgetTasks = models.PositiveSmallIntegerField(default=0)
    overdeadlineTasks = models.PositiveSmallIntegerField(default=0)

    completedTasks = models.PositiveSmallIntegerField(default=0)
    
    def __str__(self):
        return self.projectID
    
    

class Resource(models.Model):
    resourceID = models.SlugField(primary_key=True, max_length=10)
    name = models.CharField(max_length=64)
    status = models.CharField(max_length=1, default='A', 
        choices=[('A', 'Available'), ('P', 'Request Pending'), ('B', 'Booked')])
    bookingPurpose = models.TextField(blank=True, null=True)
    bookingType = models.CharField(blank=True, max_length=2, null=True,
        choices=[('EM', 'Employee'), ('TM', 'Team')]
    )
    bookedByID = models.SlugField(blank=True, max_length=10, null=True)
    bookedByName = models.CharField(blank=True, max_length=64, null=True)
    bookedFrom = models.DateTimeField(blank=True, null=True)
    bookedTill = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(blank=True)


    def __str__(self):
        return self.resourceID
