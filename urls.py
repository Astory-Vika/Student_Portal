from django.urls import path
from django.contrib import admin
from . import views
from django.views.generic import TemplateView
from .views import CustomLoginView, CustomLogoutView, student_schedule, subject_detail #, CustomRegisterView

urlpatterns = [
    # views.home => views.py - def home(request):
    path('', views.home, name='home'),

    #from student
#    path('admin', admin.site.urls),
    path('profile', views.profile, name='profile'),

    path('login', CustomLoginView.as_view(), name='login'),
    path('logout', CustomLogoutView.as_view(), name='logout'),
    path('schedule/', views.student_schedule, name='schedule'),
    path('subject-detail/<int:subject_id>/', subject_detail, name='subject_detail'),
    path('submit_homework/<int:task_id>/', views.submit_homework, name='submit_homework'),


   # path('register', CustomRegisterView.as_view(), name='register'),

    path('notes', views.notes, name='notes'),
    path('homework', views.homework, name='homework'),
    path('conversion', views.conversion, name='conversion'),
    path('todo', views.todo, name='todo'),
    path('wiki', views.wiki, name='wiki'),
    path('youtube', views.youtube, name='youtube'),
    path('dictionary', views.dictionary, name='dictionary'),
    path('books', views.books, name='books'),

    path('notes_detail/<int:pk>',
         views.NotesDetailView.as_view(), name="notes_detail"),
    path('delete_homework/<int:pk>', views.delete_homework, name='delete-homework'),
    path('delete_note/<int:pk>', views.delete_note, name='delete-note'),
    path('delete_todo/<int:pk>', views.delete_todo, name='delete-todo'),
    path('update_todo/<int:pk>', views.update_todo, name='update-todo'),
    path('update_homework/<int:pk>', views.update_homework, name='update-homework'),
]
