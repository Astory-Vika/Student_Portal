# внутрішній_каталог_додатку/management/commands/fill_users.py
#Після цього ви зможете викликати цю команду з терміналу, використовуючи python manage.py fill_db, і вона виконає ваш код

from django.core.management.base import BaseCommand
from django.utils import timezone

from django.contrib.auth.models import User
from dashboard.models import StudentGroups, StudentGroupLinks, Subjects

# Додавання груп студентів
group_data = [
    {'title': 'КН-101'},
    {'title': 'КН-102'},
    {'title': 'КН-103'},
    {'title': 'КН-104'},
    {'title': 'КН-105'}
    # додайте інші групи тут
]
# Додавання предметів
subject_data = [
    {'title': 'Математичний аналіз'},
    {'title': 'Теорія ймовірностей та математична статистика'},
    {'title': 'Програмування на мові Python'},
    {'title': 'Основи програмування'},
    {'title': 'Дискретна математика'},
    {'title': 'Програмування на C#'},
    {'title': 'Алгоритми і структури даних'},
    {'title': 'Лінійна алгебра та аналітична геометрія'},
    {'title': 'Комп''ютерна схемотехніка та архітектура комп''ютера'},
    {'title': 'Web-розробка клієнтської частини'},
    {'title': 'Організація баз даних та знань'},
    {'title': 'Web-розробка серверної частини'},
    {'title': 'Oснови Data Science'},
    {'title': 'Web-додатки на React'},
    {'title': 'Розробка ігрових додатків'},
    {'title': 'Сучасне об''єктно-орієнтоване програмування'},
    {'title': 'Комп’ютерні мережі'},
    {'title': 'Програмування додатків для мобільних пристроїв'},
    {'title': 'Тестування програмного забезпечення'},
    {'title': 'Технології захисту інформації в комп''ютерних системах'},
    {'title': 'Управління ІТ-проєктами'},
    {'title': 'Технології колективної роботи над проєктом'},
    {'title': 'Інтелектуальні інформаційні системи'}
    # додайте інші предмети тут
]


class Command(BaseCommand):
    help = 'Заповнення таблиці StudentGroups за допомогою Django ORM'  #python manage.py fill_db --help - виклик допомоги

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)

        for data in group_data:
            group = StudentGroups.objects.create(title=data['title'])
            group.save()

        # Отримуємо всі записи Users, які є студентами
        students = User.objects.filter(staffs__role='student')
        # Отримуємо всі групи студентів
        groups = StudentGroups.objects.all()
        # Індекс для розподілу студентів по групах
        group_index = 0

        # Ітеруємося по студентам
        for student in students:
            # Отримуємо поточну групу
            current_group = groups[group_index]

            # Створюємо запис про зв'язок між студентом та групою
            student_group_link = StudentGroupLinks.objects.create(user=student, group=current_group)
            student_group_link.save()

            # Збільшуємо індекс групи
            group_index = (group_index + 1) % len(groups)

            # Виводимо повідомлення про успішне розподілення
            self.stdout.write(
                self.style.SUCCESS(f"Студент {student.username} розподілено до групи {current_group.title}"))

        for data in subject_data:
          subject = Subjects.objects.create(title=data['title'])
          subject.save()


