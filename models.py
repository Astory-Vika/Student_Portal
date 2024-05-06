from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
# Create your models here.

#модель для розширення User
class Staffs(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=(('admin', 'Admin'), ('teacher', 'Teacher'), ('student', 'Student')), default='student')
    def __str__(self):
        return '%s %s %s - login: "%s" - role: "%s"' % (self.user.first_name.title(), self.middle_name, self.user.last_name.title(), self.user.username, self.role)
    class Meta:
        verbose_name = 'Інф. користувача' #напис в адмін-панелі однина
        verbose_name_plural = 'Інф. користувачів' #напис в адмін-панелі множина


class StudentGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Група студентів' #напис в адмін-панелі однина
        verbose_name_plural = 'Групи студентів' #напис в адмін-панелі множина


class StudentGroupLinks(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(StudentGroups, on_delete=models.CASCADE)
    def __str__(self):
        return '<%s> %s %s - login: "%s"' % (self.group.title, self.user.first_name.title(), self.user.last_name.title(), self.user.username)
    class Meta:
        verbose_name = 'Зв''язок студент-група' #напис в адмін-панелі однина
        verbose_name_plural = 'Зв''язки студент-група' #напис в адмін-панелі множина


class Subjects(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Дисципліна' #напис в адмін-панелі однина
        verbose_name_plural = 'Дисципліни' #напис в адмін-панелі множина


class TeachingAssignments(models.Model):
    id = models.BigAutoField(primary_key=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    group = models.ForeignKey(StudentGroups, on_delete=models.CASCADE)
    def __str__(self):
        return '<%s> - "%s" - %s %s %s - login: "%s"' % (self.group.title, self.subject.title, self.teacher.first_name.title(), self.teacher.staffs.middle_name, self.teacher.last_name.title(), self.teacher.username)
    class Meta:
        verbose_name = 'Зв''язок викладач-предмет-група' #напис в адмін-панелі однина
        verbose_name_plural = 'Зв''язки викладач-предмет-група' #напис в адмін-панелі множина


class Schedule(models.Model):
    id = models.BigAutoField(primary_key=True)
    teaching_assignments = models.ForeignKey(TeachingAssignments, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=20, choices=(('Пн', 'Понеділок'), ('Вт', 'Вівторок'), ('Ср', 'Середа'), ('Чт', 'Четвер'), ('Пт', 'П''ятниця')), default='Пн')
    class_num = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)], default=1) #номер заняття - розраховуємо на 7 занять в день, не прив'язуємо до часу бо тривалість і перерви можуть мінятись
    comment = models.CharField(max_length=200) #коментар в розкладі (номер аудиторії, інші особливості)
    def __str__(self):
        return '<%s> - "%s" - %s %s %s - день: "%s" - номер заняття: "%s" - коментар: "%s"' % (self.teaching_assignments.group.title, self.teaching_assignments.subject.title,
                                                               self.teaching_assignments.teacher.first_name.title(), self.teaching_assignments.teacher.staffs.middle_name, 
                                                               self.teaching_assignments.teacher.last_name.title(),
                                                               self.day_of_week, self.class_num, self.comment)
    class Meta:
        verbose_name = 'Запис в розкладі занять' #напис в адмін-панелі однина
        verbose_name_plural = 'Розклад занять' #напис в адмін-панелі множина


class Notes(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Нотатки' #напис в адмін-панелі однина
        verbose_name_plural = 'Нотатки' #напис в адмін-панелі множина


class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    group = models.ForeignKey(StudentGroups, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    startdate = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Призначене завдання' #напис в адмін-панелі однина
        verbose_name_plural = 'Призначені завдання' #напис в адмін-панелі множина


class Homework(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    title = models.CharField(max_length=100) #текст-заголовок на домашнє завдання
    description = models.TextField() #текст-відповідь на домашнє завдання
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)  #оцінка викладача за виконане завдання
    gradedescription = models.TextField()  #опис оцінки викладача за виконане завдання
    finishdate = models.DateTimeField()  #коли завдання було завершене
    is_finished = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Завдання в роботі' #напис в адмін-панелі однина
        verbose_name_plural = 'Завдання в роботі' #напис в адмін-панелі множина


class Todo(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    is_finished = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Справа на виконання' #напис в адмін-панелі однина
        verbose_name_plural = 'Перелік справ' #напис в адмін-панелі множина