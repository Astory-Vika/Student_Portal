from django.contrib import admin
from .models import *

#реєструємо моделі, щоб вони з'явились в адмін-панелі
admin.site.register(Staffs)
admin.site.register(StudentGroups)
admin.site.register(StudentGroupLinks)
admin.site.register(Subjects)
admin.site.register(TeachingAssignments)
admin.site.register(Schedule)
admin.site.register(Notes)
admin.site.register(Task)
admin.site.register(Homework)
admin.site.register(Todo)


