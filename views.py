from datetime import timezone
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, render, redirect
from django.shortcuts import get_object_or_404
from .forms import *

import requests
from youtubesearchpython import VideosSearch
import wikipedia
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm #, UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views import generic
#from django.views.generic import CreateView
from .models import Notes, Task, Todo, StudentGroupLinks, Schedule, Subjects, Homework, StudentGroups, User




class CustomLoginView(LoginView):
    template_name = 'dashboard/custom_login.html'
    authentication_form = AuthenticationForm

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


#class CustomRegisterView(CreateView):
#    template_name = 'dashboard/register.html' #'dashboard/custom_register.html'
#    #context =  'u_form';
#    form_class = UserRegisterForm
#    success_url = reverse_lazy('login')

#@login_required
def home(request):
    role = None
    username = None
    if request.user.is_authenticated:
        TodoList = Todo.objects.all()

        username = request.user.username
        try:
            staff = Staffs.objects.get(user=request.user)
            role = staff.role
        except Staffs.DoesNotExist:
            role = None

        try:
            # Припускаємо, що студенти пов'язані з групою через модель StudentGroupLinks
            student_group_link = StudentGroupLinks.objects.get(user=request.user)
            # Отримуємо всі викладацькі призначення для групи студента
            assignments = TeachingAssignments.objects.filter(group=student_group_link.group)
            subjects_details = [{
                'subject_id': assignment.subject.id,  # Include subject_id
                'subject_title': assignment.subject.title,
                'teacher_last_name': assignment.teacher.last_name,
                'teacher_middle_name': Staffs.objects.get(user=assignment.teacher).middle_name  # Якщо middle_name зберігається в моделі Staffs
            } for assignment in assignments]

            context = {'title': f'Головна сторінка сайту - Користувач: {username} Роль: {role}', 'todo': TodoList,
                       'subjects_details': subjects_details}

            #return render(request, 'dashboard/home.html', {'subjects_details': subjects_details})
            return render(request, 'dashboard/home.html', context)
        except StudentGroupLinks.DoesNotExist:
            context = {'title': f'Головна сторінка сайту - Користувач: {username} Роль: {role}', 'todo': TodoList,
                       'error': 'You are not assigned to any group'}
            #return render(request, 'dashboard/home.html', {'error': 'You are not assigned to any group'})
            return render(request, 'dashboard/home.html', context)
    else:
#        ---return redirect('login')
#        return render(request, 'dashboard/home.html');
        context = {'title': f'Головна сторінка сайту - Користувач: {username} Роль: {role}'}
        return render(request, 'dashboard/home.html', context)
"""
#@login_required
def home(request):
    if request.user.is_authenticated:
        try:
            # Припускаємо, що студенти пов'язані з групою через модель StudentGroupLinks
            student_group_link = StudentGroupLinks.objects.get(user=request.user)
            # Отримуємо всі викладацькі призначення для групи студента
            assignments = TeachingAssignments.objects.filter(group=student_group_link.group)
            subjects_details = [{
                'subject_title': assignment.subject.title,
                'teacher_last_name': assignment.teacher.last_name,
                'teacher_middle_name': Staffs.objects.get(user=assignment.teacher).middle_name  # Якщо middle_name зберігається в моделі Staffs
            } for assignment in assignments]
            return render(request, 'dashboard/home.html', {'subjects_details': subjects_details})
        except StudentGroupLinks.DoesNotExist:
            return render(request, 'dashboard/home.html', {'error': 'You are not assigned to any group'})
    else:
        return redirect('login')
"""

def register(request):
    if request.method == "POST":
        u_form = UserRegisterForm(request.POST)

        if u_form.is_valid():
            u_form.save()

            username = u_form.cleaned_data.get('username')
            messages.success(request, f'Акаунт створено для {username}!')
            return redirect('login')
        else:
            messages.error(request, ('Будь ласка, виправте помилки.'))

    else:
        u_form = UserRegisterForm()
    return render(request, 'dashboard/register.html', {'u_form': u_form})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Staffs, StudentGroupLinks, TeachingAssignments, Schedule

@login_required
def student_schedule(request):
    user = request.user

    # Спробуйте використати 'select_related' та 'prefetch_related' для оптимізації запитів
    try:
        staff = Staffs.objects.select_related('user').get(user=user, role='student')
        student_group_link = StudentGroupLinks.objects.select_related('group').get(user=user)
        teaching_assignments = TeachingAssignments.objects.filter(group=student_group_link.group).prefetch_related('subject', 'teacher')
        schedules = Schedule.objects.filter(teaching_assignments__in=teaching_assignments).order_by('day_of_week', 'class_num')
    except Staffs.DoesNotExist:
        messages.error(request, 'У вас немає прав доступу як для студента.')
        return redirect('home')  # Redirect to home page if the user is not a student
    except StudentGroupLinks.DoesNotExist:
        messages.error(request, 'У вас немає призначеної групи.')
        return redirect('home')  # Redirect to home page if the student has no group

    context = {
        'schedules': schedules,
        'user': user
    }
    return render(request, 'dashboard/schedule.html', context)

def subject_detail(request, subject_id):
    # Отримуємо всі викладацькі завдання, пов'язані з вказаним subject_id
    teaching_assignments = get_list_or_404(TeachingAssignments, subject_id=subject_id)
    
    tasks = Task.objects.filter(subject_id=subject_id)
    homeworks = []
    if request.user.is_authenticated:
        homeworks = Homework.objects.filter(user=request.user, task__subject_id=subject_id)

    
    context = {
        'teaching_assignments': teaching_assignments,
        'tasks': tasks,
        'homeworks': homeworks
    }

    return render(request, 'dashboard/subject_detail.html', context)



@login_required
def submit_homework(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = HomeworkResponseForm(request.POST)
        if form.is_valid():
            homework_response = form.save(commit=False)
            homework_response.user = request.user
            homework_response.task = task
            homework_response.is_submitted = True
            homework_response.submission_date = timezone.now()
            homework_response.save()
            messages.success(request, 'Your response has been submitted!')
            return redirect('some-view')
    else:
        form = HomeworkResponseForm()
    return render(request, 'dashboard/submit_homework.html', {'form': form})





@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)
    if len(homeworks) == 0:
        homeworks_done = True
    else:
        homeworks_done = False
    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'homeworks': zip(homeworks, range(1, len(homeworks)+1)),
        'todos': zip(todos, range(1, len(todos)+1)),
        'homeworks_done': homeworks_done,
        'todos_done': todos_done,
    }
    return render(request, 'dashboard/profile.html', context)


@ login_required
def notes(request):
    if request.method == "POST":
        form = ModelForm(request.POST)
        if form.is_valid():
            notes = Notes(
                user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
            messages.success(
                request, f'Notes Added from {request.user.username}!')
    else:
        form = ModelForm()
    notes = Notes.objects.filter(user=request.user)

    context = {'form': form, 'notes': notes}
    return render(request, 'dashboard/notes.html', context)



@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            #homeworks = Homework(user=request.user, subject=request.POST['subject'], title=request.POST['title'], description=request.POST['description'], due=request.POST['due'], is_finished=finished)
            #homeworks.save()
            messages.success(
                request, f'Homework Added from {request.user.username}!')
    else:
        form = HomeworkForm()
    homeworks = Homework.objects.filter(user=request.user)
    if len(homeworks) == 0:
        homeworks_done = True
    else:
        homeworks_done = False
    homeworks = zip(homeworks, range(1, len(homeworks)+1))
    context = {'form': form, 'homeworks': homeworks,
               'homeworks_done': homeworks_done}
    return render(request, 'dashboard/homework.html', context)


@login_required
def todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user=request.user, title=request.POST['title'], is_finished=finished)
            todos.save()
            messages.success(
                request, f'Todo Added from {request.user.username}!')
    else:
        form = TodoForm()
    todos = Todo.objects.filter(user=request.user)

    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False
    todos = zip(todos, range(1, len(todos)+1))
    context = {'form': form, 'todos': todos, 'todos_done': todos_done}
    return render(request, 'dashboard/todo.html', context)


def dictionary(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)

        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms,
            }
        except:
            context = {
                'form': form,
                'input': '',
            }
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardForm()
    return render(request, 'dashboard/dictionary.html', {'form': form})


def wiki(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form': form,
            'title': search.title,
            'link': search.url,
            'details': search.summary,
        }
        return render(request, 'dashboard/wiki.html', context)
    else:
        form = DashboardForm()
    return render(request, 'dashboard/wiki.html', {'form': form})



def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        videos = VideosSearch(text, limit=5)
        result_list = []
        print(videos.result())
        for i in videos.result()['result']:
            result_dict = {
                'input': text,
                'title': i['title'],
                'duration': i['duration'],
                'thumbnail': i['thumbnails'][0]['url'],
                'channel': i['channel']['name'],
                'link': i['link'],
                'views': i['viewCount']['short'],
                'published': i['publishedTime'],
            }
            desc = ''

            for j in i['descriptionSnippet']:
                desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
        return render(request, 'dashboard/youtube.html', {'form': form, 'results': result_list})
    else:
        form = DashboardForm()
    return render(request, 'dashboard/youtube.html', {'form': form})


def conversion(request):
    if request.method == "POST":
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} yard = {int(input)*3} foot'
                    if first == 'foot' and second == 'yard':
                        answer = f'{input} foot = {int(input)/3} yard'
                context = {'form': form, 'm_form': measurement_form,
                           'input': True, 'answer': answer}

        if request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input} pound = {int(input)*0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int(input)*2.20462} pound'
                context = {'form': form, 'm_form': measurement_form,
                           'input': True, 'answer': answer}

    else:
        form = ConversionForm()
        context = {'form': form, 'input': False}
    return render(request, 'dashboard/conversion.html', context)


def books(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'title': answer['items'][i]['volumeInfo']['title'],
                'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                'description': answer['items'][i]['volumeInfo'].get('description'),
                'count': answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories': answer['items'][i]['volumeInfo'].get('categories'),
                'rating': answer['items'][i]['volumeInfo'].get('averageRating'),
                'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview': answer['items'][i]['volumeInfo'].get('previewLink')
            }
            result_list.append(result_dict)

        context = {
            'form': form,
            'results': result_list,
        }
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()
    return render(request, 'dashboard/books.html', {'form': form})


def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('homework')


def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('homework')


def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect('notes')


def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('todo')


def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('todo')


class NotesDetailView(generic.DetailView):
    model = Notes
