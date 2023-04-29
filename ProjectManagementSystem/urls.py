"""ProjectManagementSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from ProjectManagementSystemApp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.Landing, name='Landing'),
    path('login/', views.Login, name='Login'),
    path('logout/', views.Logout, name='Logout'),
    
    path('create-project/', views.CreateProject, name='CreateProject'),
    path('edit-project/<slug:projectID>', views.EditProject, name='EditProject'),
    path('view-projects/', views.ViewProjects, name='ViewProjects'),
    path('project-dashboard/<slug:projectID>', views.ProjectDashboard, name='ProjectDashboard'),
    path('project-complete/<slug:projectID>', views.MarkProjectAsCompleted, name='MarkProjectAsCompleted'),
    path('delete-project/<slug:projectID>', views.DeleteProject, name='DeleteProject'),

    path('manage-teams/', views.ManageTeams, name='ManageTeams'),
    path('team-dashboard/<slug:teamID>', views.TeamDashboard, name='TeamDashboard'),

    path('create-team/', views.CreateTeam, name='CreateTeam'),
    path('edit-members/<slug:teamID>', views.EditMembers, name='EditMembers'),

    path('create-task/<slug:projectID>', views.CreateTask, name='CreateTask'),
    path('task-dashboard/<slug:taskID>', views.TaskDashboard, name='TaskDashboard'),
    path('delete-task/<slug:taskID>', views.DeleteTask, name='DeleteTask'),
  
    path('resources/', views.ManageResources, name='Resources'),
    path('create-resource/', views.CreateResource, name='CreateResource'),
    path('delete-resource/<slug:resourceID>', views.DeleteResource, name='DeleteResource'),
    path('resource-booking-request/<slug:resourceID>', views.RequestResource, name='RequestResource'),

    path('tinymce/', include('tinymce.urls')),
]