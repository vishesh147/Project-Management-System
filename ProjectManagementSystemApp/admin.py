from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Project)
admin.site.register(Employee)
admin.site.register(Team)
admin.site.register(Task)
admin.site.register(Resource)