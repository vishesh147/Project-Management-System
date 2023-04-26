from django.shortcuts import render, redirect
from .models import *
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.forms.models import model_to_dict
from django.views.decorators.cache import cache_control
from django.contrib import messages


# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Landing(request):
    if request.user.is_authenticated:
        if request.session['employee']['role'] == 'RM':
            return redirect('Resources')
        else:
            return redirect('ViewProjects')
        
    return render(request, 'landing.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Login(request):
    if request.user.is_authenticated:
        return redirect('Landing')
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            request.session.set_expiry(0)
            employee = model_to_dict(Employee.objects.get(employeeID=request.POST['username']))
            employee['joiningDate'] = employee['joiningDate'].strftime("%d-%m-%Y")
            request.session['employee'] = employee
            login(request, user)
            return redirect('Landing')
        else:
            messages.error(request, "Invalid employee ID or password. Please try again.")
            return redirect('Login')
    return render(request, 'login.html')


def Logout(request):
    request.session.flush()
    logout(request)
    return redirect('Landing')



# Only for Owner
@login_required
def CreateTeam(request):
    if request.session['employee']['role'] != 'O':
        raise PermissionDenied
    if request.method == "POST":
        manager = request.POST['manager'].split('-')

        if request.POST.get('teamID', ''):
            team = Team.objects.get(teamID=request.POST['teamID'])
            team.name = request.POST['name']
            team.description = request.POST['description']
            team.managerID = manager[1]
            team.managerName = manager[0]
            team.save()
            messages.success(request, team.teamID + ' : Team Updated Successfully.')
            return redirect(reverse("TeamDashboard", kwargs={"teamID": team.teamID}))

        timestamp = datetime.now()
        while Team.objects.filter(teamID="T"+timestamp.strftime("%H%M%S")):
            timestamp = datetime.now()

        team = Team(
            teamID="T"+timestamp.strftime("%H%M%S"),
            name=request.POST['name'],
            managerID=manager[1],
            managerName=manager[0],
            description=request.POST['description'],
        )
        team.save()
        messages.success(request, 'New Team Created Successfully.')

    return redirect("ManageTeams")



# Owner and Project Manager
@login_required
def ManageTeams(request):
    userRole = request.session['employee']['role']
    if userRole != 'O' and userRole != 'PM' and userRole != 'RM':
        raise PermissionDenied

    if userRole == 'O' or userRole == 'RM':
        teams = Team.objects.all()
    else:
        teams = Team.objects.filter(managerID=request.session['employee']['employeeID'])

    managers = Employee.objects.filter(role='PM')
    return render(request, 'team/manageTeams.html', {'teams':teams, 'managers':managers})


# Owner, PM and Employee
@login_required
def TeamDashboard(request, teamID):
    userRole = request.session['employee']['role']
    if userRole != 'O' and userRole != 'PM' and userRole != 'E':
        raise PermissionDenied
    
    try: 
        team = Team.objects.get(teamID=teamID)
    except:
        raise ObjectDoesNotExist
    
    if userRole == 'PM' and team.managerID != request.session['employee']['employeeID']:
        raise PermissionDenied   

    managers = Employee.objects.filter(role='PM')
    members = Employee.objects.filter(teamID=teamID, role='E')
    ongoingProjects = Project.objects.filter(teamID=teamID, status='O')
    completedProjects = Project.objects.filter(teamID=teamID, status='C')
    freeEmployees = Employee.objects.filter(teamID__isnull=True, role='E')
    return render(request, 'team/teamDashboard.html', {'team':team, 'managers':managers, 'members':members, 'freeEmployees':freeEmployees, 
                 'teamProjects':[("ongoing", "info", ongoingProjects),
                                 ("completed", "success", completedProjects)]})


# Owner, Project Manager
@login_required
def EditMembers(request, teamID):
    userRole = request.session['employee']['role']
    if userRole != 'O' and userRole != 'PM':
        raise PermissionDenied
    
    try: 
        team = Team.objects.get(teamID=teamID)
    except:
        raise ObjectDoesNotExist

    if userRole != 'O' and team.managerID != request.session['employee']['employeeID']:
        raise PermissionDenied   

    if request.method == "POST":
        if request.POST['type'] == 'add':
            count = 0
            toBeAdded = list(request.POST.keys())
            freeEmployees = Employee.objects.filter(teamID__isnull=True, role='E')
            for freeEmployee in freeEmployees:
                if freeEmployee.employeeID in toBeAdded:
                    freeEmployee.teamID = team.teamID
                    freeEmployee.teamName = team.name
                    freeEmployee.managerID = team.managerID
                    freeEmployee.managerName = team.managerName
                    freeEmployee.save()
                    count = count + 1
            team.size = team.size + count
            team.save()
        else:
            count = 0
            toBeRemoved = list(request.POST.keys())
            teamMembers = Employee.objects.filter(teamID=teamID, role='E')
            for teamMember in teamMembers:
                if teamMember.employeeID in toBeRemoved:
                    teamMember.teamID = None
                    teamMember.teamName = ""
                    teamMember.managerID = None
                    teamMember.managerName = ""
                    teamMember.save()
                    count = count + 1
            team.size = team.size - count
            team.save()
        messages.success(request, 'Team updated successfully.')

    
    return redirect(reverse("TeamDashboard", kwargs={"teamID": teamID}))



# Only for Owner
@login_required
def CreateProject(request):
    if request.session['employee']['role'] != 'O':
        raise PermissionDenied
    teams = Team.objects.all()
    if request.method == "POST":
        timestamp = datetime.now()
        team = teams.get(teamID=request.POST['team'])
        project = Project(
            projectID="PRJ"+timestamp.strftime("%d%m%y%H%M%S"),
            title=request.POST['title'],
            client=request.POST['client'],
            description=request.POST['description'],
            allocatedBudget=request.POST['budget'],
            deadline=request.POST['deadline'],
            teamID=team.teamID,
            teamName=team.name,
            managerID=team.managerID,
            managerName=team.managerName,
            status='O'
        )
        project.save()
        messages.success(request, 'Project Created Successfully.')
        return redirect('ViewProjects')
    return render(request, 'project/createProject.html', {'teams':teams})


@login_required
def EditProject(request, projectID):
    if request.session['employee']['role'] != 'O':
        raise PermissionDenied
    try:
        project = Project.objects.get(projectID=projectID)
    except:
        raise ObjectDoesNotExist
    
    teams = Team.objects.all()
    if request.method == "POST":
        team = teams.get(teamID=request.POST['team'])
        project.title = request.POST['title']
        project.client = request.POST['client']
        project.description = request.POST['description']
        project.allocatedBudget = request.POST['budget']
        project.deadline = request.POST['deadline']
        project.teamID = team.teamID
        project.teamName = team.name
        project.managerID = team.managerID
        project.managerName = team.managerName
        project.save()
        messages.success(request, project.projectID + ' : Project Edited Successfully.')

        return redirect('ViewProjects')
    return render(request, 'project/createProject.html', {'teams':teams, 'project':project})



# As per employee type. PM, RM, E(Team-wise), Owner (All)  
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ViewProjects(request):
    userRole = request.session['employee']['role']
    if userRole != 'O' and userRole != 'PM' and userRole != 'E':
        raise PermissionDenied
    
    if userRole == 'O':
        ongoingProjects = Project.objects.filter(status='O')
        completedProjects = Project.objects.filter(status='C')
    elif userRole == 'PM':
        ongoingProjects = Project.objects.filter(status='O', managerID=request.session['employee']['employeeID'])
        completedProjects = Project.objects.filter(status='C', managerID=request.session['employee']['employeeID'])
    elif userRole == 'E':
        ongoingProjects = Project.objects.filter(status='O', teamID=request.session['employee']['teamID'])
        completedProjects = Project.objects.filter(status='C', teamID=request.session['employee']['teamID'])

    return render(request, 'project/viewProjects.html', {'ongoingProjects':ongoingProjects, 'completedProjects':completedProjects})


@login_required
def ProjectDashboard(request, projectID):
    userRole = request.session['employee']['role']
    if userRole != 'O' and userRole != 'PM' and userRole != 'E':
        raise PermissionDenied
    
    try: 
        project = Project.objects.get(projectID=projectID)
    except:
        raise ObjectDoesNotExist

    if userRole == 'PM' and request.session['employee']['employeeID'] != project.managerID:
        raise PermissionDenied

    if userRole == 'E' and request.session['employee']["teamID"] != project.teamID:
        raise PermissionDenied

    teamMembers = Employee.objects.filter(role='E', teamID=project.teamID)

    inprogressTasks = Task.objects.filter(projectID=projectID, status='I')
    completedTasks = Task.objects.filter(projectID=projectID, status='C')
    submittedForReviewTasks = Task.objects.filter(projectID=projectID, status='R')
    
    tasksByStatus = None
    totalTasks = inprogressTasks.count() + completedTasks.count() + submittedForReviewTasks.count()
    completionPercentage = None

    if userRole == 'E':
        employeeID = request.session['employee']['employeeID']
        inprogressTasks = inprogressTasks.filter(projectID=projectID, status='I', employeeID=employeeID)
        completedTasks = completedTasks.filter(projectID=projectID, status='C', employeeID=employeeID)
        submittedForReviewTasks = submittedForReviewTasks.filter(projectID=projectID, status='R', employeeID=employeeID)
    else:
        tasksByStatus = [len(x) for x in [inprogressTasks, submittedForReviewTasks, completedTasks]]
        if sum(tasksByStatus):
            completionPercentage = 100 *( tasksByStatus[-1]/sum(tasksByStatus))
        
    
    return render(request, 'project/projectDashboard.html', {'project':project, 'teamMembers':teamMembers, 
                    'tasksByStatus' : tasksByStatus, 'completionPercentage': completionPercentage, 'totalTasks': totalTasks,
                    'inprogress': inprogressTasks,
                    'completed':completedTasks,
                    'review':submittedForReviewTasks})



@login_required
def CreateTask(request, projectID):
    try: 
        project = Project.objects.get(projectID=projectID)
    except:
        raise ObjectDoesNotExist
    
    userRole = request.session['employee']['role']
    if userRole != 'O' and userRole != 'PM':
        raise PermissionDenied
    
    if userRole == 'PM' and request.session['employee']['employeeID'] != project.managerID:
        raise PermissionDenied

    if request.method == "POST":
        assignee = request.POST['assignee'].split('-')
        if request.POST.get('taskID', ''):
            task = Task.objects.get(taskID=request.POST['taskID'])
            task.title = request.POST['title']
            task.description = request.POST['description']
            task.allocatedBudget = request.POST['budget']
            task.deadline = request.POST['deadline']
            task.employeeID = assignee[1]
            task.employeeName = assignee[0]
            task.save()
            messages.success(request, 'Task updated successfully.')
            return redirect(reverse("TaskDashboard", kwargs={"taskID": task.taskID}))
        
        timestamp = datetime.now()        
        task = Task(
            taskID="TSK"+timestamp.strftime("%d%m%y%H%M%S"),
            title=request.POST['title'],
            allocatedBudget=request.POST['budget'],
            description=request.POST['description'],
            employeeID=assignee[1],
            employeeName=assignee[0],
            deadline=request.POST['deadline'],
            assigned=timestamp,
            projectID=projectID,
            managerID=project.managerID,
            teamID=project.teamID,
            status='I'
        )
        task.save()
        messages.success(request, 'Task '+ task.taskID + ' created successfully.')

    return redirect(reverse("ProjectDashboard", kwargs={"projectID": projectID}))



@login_required
def TaskDashboard(request, taskID):
    try:
        task = Task.objects.get(taskID=taskID)
    except:
        raise ObjectDoesNotExist
    
    # Access only to Owner, Project Manger or Employee
    userRole = request.session['employee']['role']
    if userRole != 'O' and userRole != 'PM' and userRole != 'E':
        raise PermissionDenied
    
    if userRole == 'PM' and request.session['employee']['employeeID'] != task.managerID:
        raise PermissionDenied
    
    if userRole == 'E' and request.session['employee']['employeeID'] != task.employeeID:
        raise PermissionDenied

    teamMembers = Employee.objects.filter(role='E', teamID=task.teamID)
    reportForm = ReportForm(instance=task)
    if request.method == "POST":
        if request.POST.get('review', '') == 'approved':
            if request.session['employee']['employeeID'] != task.managerID:
                raise PermissionDenied
            task.status = 'C'
            task.completed = timezone.now()
            print(request.POST)
            task.rating = request.POST.get('rating', '')
            task.save()
            # Update employee rating
            employee = Employee.objects.get(employeeID=task.employeeID)
            employee.updateRating()
            employee.save()
            # Update project budget
            project = Project.objects.get(projectID=task.projectID)
            project.utilizedBudget += task.utilizedBudget

            if (task.deadline) < (task.completed):
                project.overdeadlingTasks += 1
            
            if task.utilizedBudget < task.allocatedBudget:
                project.overbudgetTasks += 1
            
            project.completedTasks += 1
            project.save()
            messages.success(request, task.taskID + ' : Task Report Approved.')
            return redirect(reverse("ProjectDashboard", kwargs={"projectID":task.projectID}))

        reportForm = ReportForm(request.POST, instance=task)
        if reportForm.is_valid():
            # Task submission
            task = reportForm.save()
            task.status = 'R'
            task.submitted = datetime.now()
            task.save()
            messages.success(request, task.taskID + ' : Task Report Rejected.')
            return redirect(reverse("ProjectDashboard", kwargs={"projectID":task.projectID}))
    return render(request, 'task/taskDashboard.html', {'form': reportForm, 'task':task, 'teamMembers':teamMembers})



@login_required
def CreateResource(request):
    userRole = request.session['employee']['role']
    if userRole != 'O' and userRole != 'RM':
        raise PermissionDenied
    
    if request.method == "POST":
        timestamp = datetime.now()
        while Resource.objects.filter(resourceID="R"+timestamp.strftime("%H%M%S")):
            timestamp = datetime.now()

        resource = Resource(
            resourceID="R"+timestamp.strftime("%H%M%S"),
            name=request.POST['name'],
            created=timestamp
        )
        resource.save()
        messages.success(request, 'New resource added successfully.')

    return redirect("Resources")


def RequestResource(request, resourceID):
    userRole = request.session['employee']['role']
    if userRole != 'O' and userRole != 'PM' and userRole != 'E':
        raise PermissionDenied
        
    try:
        resource = Resource.objects.get(resourceID=resourceID)
    except:
        ObjectDoesNotExist

    teams = None
    if userRole == 'PM':
        teams = Team.objects.filter(managerID=request.session['employee']['employeeID'])

    if request.method == "POST":
        resource.status = 'P'
        resource.bookingPurpose = request.POST['purpose']
        resource.bookingType = request.POST['bookingType']
        if resource.bookingType == 'EM':
            resource.bookedByID = request.session['employee']['employeeID']
            resource.bookedByName = request.session['employee']['name']
        else:
            resource.bookedByID = request.session['employee']['teamID']
            resource.bookedByName = request.session['employee']['teamName']

        resource.bookedFrom = request.POST['from']
        resource.bookedTill = request.POST['till']
        resource.save()
        messages.success(request, 'Resource Request Successful.')
        return redirect('Resources')

    return render(request, 'resource/requestResource.html', {'resource':resource, 'teams':teams})


def ManageResources(request):
    userRole = request.session['employee']['role']
    if userRole != 'O' and userRole != 'PM' and userRole != 'E' and userRole != 'RM':
        raise PermissionDenied
    
    if request.method == "POST":
        try:
            resource = Resource.objects.get(resourceID=request.POST['resourceID'])
        except:
            raise ObjectDoesNotExist
        
        if request.POST['action'] == 'Approve':
            resource.status = 'B'
            messages.success(request, resource.resourceID + ' : Resource Request Approved.')
        else:
            resource.status = 'A'
            resource.bookingPurpose = None
            resource.bookingType = None
            resource.bookedByID = None
            resource.bookedByName = None
            resource.bookedFrom = None
            resource.bookedTill = None
            messages.success(request, resource.resourceID + ' : Resource Request Rejected.')
                    
        resource.save()
        return redirect('Resources')
    
    availableResources = Resource.objects.filter(status='A')
    pendingResources = Resource.objects.filter(status='P')
    bookedResources = Resource.objects.filter(status='B')
    
    yourResources = None
    if userRole != 'RM':
        yourResources = Resource.objects.filter(bookedByID=request.session['employee']['employeeID'], status='B')
        
    return render(request, 'resource/manageResources.html',
            {'availableResources':availableResources,
                'bookedResources':bookedResources,
                'pendingResources':pendingResources,
                'yourResources':yourResources,
            })