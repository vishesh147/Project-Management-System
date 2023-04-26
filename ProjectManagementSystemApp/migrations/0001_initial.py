# Generated by Django 4.1.8 on 2023-04-22 15:29

import datetime
from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('employeeID', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=254)),
                ('joiningDate', models.DateField(blank=True, null=True)),
                ('salary', models.PositiveIntegerField(default=0)),
                ('role', models.CharField(choices=[('PM', 'Project Manager'), ('RM', 'Resource Manager'), ('E', 'Employee')], default='E', max_length=6)),
                ('teamID', models.CharField(blank=True, max_length=10)),
                ('teamName', models.CharField(blank=True, max_length=64)),
                ('managerID', models.CharField(blank=True, max_length=10)),
                ('managerName', models.CharField(blank=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('projectID', models.SlugField(max_length=15, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64)),
                ('client', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('allocatedBudget', models.PositiveIntegerField(blank=True)),
                ('utilizedBudget', models.PositiveIntegerField(blank=True, default=0)),
                ('deadline', models.DateTimeField()),
                ('created', models.DateTimeField(default=datetime.datetime(2023, 4, 22, 20, 59, 4, 509261))),
                ('completed', models.DateTimeField(blank=True)),
                ('status', models.CharField(choices=[('O', 'Ongoing'), ('C', 'Completed')], default='O', max_length=1)),
                ('teamID', models.CharField(blank=True, max_length=10)),
                ('teamName', models.CharField(blank=True, max_length=64)),
                ('managerID', models.CharField(blank=True, max_length=10)),
                ('managerName', models.CharField(blank=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('taskID', models.SlugField(max_length=32, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('deadline', models.DateTimeField(blank=True)),
                ('completed', models.DateTimeField(blank=True)),
                ('assigned', models.DateTimeField()),
                ('allocatedBudget', models.PositiveIntegerField()),
                ('utilizedBudget', models.PositiveIntegerField(blank=True, null=True)),
                ('report', tinymce.models.HTMLField(blank=True)),
                ('employeeID', models.CharField(max_length=10)),
                ('employeeName', models.CharField(max_length=64)),
                ('projectID', models.SlugField(max_length=15)),
                ('managerID', models.CharField(max_length=10)),
                ('status', models.CharField(choices=[('I', 'In Progress'), ('C', 'Completed'), ('R', 'Submitted For Review')], default='I', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('teamID', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(default='')),
                ('managerID', models.CharField(max_length=10)),
                ('managerName', models.CharField(max_length=64)),
                ('size', models.PositiveSmallIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]