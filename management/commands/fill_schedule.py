# внутрішній_каталог_додатку/management/commands/fill_users.py
#Після цього ви зможете викликати цю команду з терміналу, використовуючи python manage.py fill_db, і вона виконає ваш код

from django.core.management.base import BaseCommand
from django.utils import timezone
from random import randint
from dashboard.models import TeachingAssignments, Schedule

from itertools import cycle

class Command(BaseCommand):
    help = 'Заповнення таблиці Shedule за допомогою Django ORM'  #python manage.py fill_db --help - виклик допомоги

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)

        # Отримати всі записи з TeachingAssignments
        teaching_assignments = TeachingAssignments.objects.all()
        # Ітератор по об'єктам TeachingAssignments
        teaching_assignments_iterator = iter(teaching_assignments)

        # Дні тижня та години
        days_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт']
        hours = list(range(1, 8))

        # Цикл перебору днів тижня
        for day in days_of_week:
            # Цикл перебору годин
            for hour in hours:
                # Перевірити, чи є ще записи в teaching_assignments
                try:
                    assignment = next(teaching_assignments_iterator)
                except StopIteration:
                    # Якщо дійшли до кінця, починаємо з початку
                    teaching_assignments_iterator = iter(teaching_assignments)
                    assignment = next(teaching_assignments_iterator)

                # Створити коментар для розкладу
                comment = 'Аудиторія {}'.format(randint(100, 200))
                # Створити запис розкладу
                schedule_entry = Schedule.objects.create(
                                    teaching_assignments=assignment,
                                    day_of_week=day,
                                    class_num=hour,
                                    comment=comment
                                )
                schedule_entry.save()