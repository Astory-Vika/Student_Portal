# внутрішній_каталог_додатку/management/commands/fill_users.py
#Після цього ви зможете викликати цю команду з терміналу, використовуючи python manage.py fill_db, і вона виконає ваш код

# викладачі - Users id від 3 до 10 включно, 5 груп від 1 до 5 включно, предмети 23 шт (група 1 - з 1 по 5 предмет, група 2 - 6-10 предмет, група 3 - 11-15 предмет, група 4 - 16-19 предмет, група 5 - 20-23 предмет) . Викладач Users id = 3  - предмет 1 - група 1, предмет 2 - група 1,  предмет 3-група 1; Users id = 4 - предмет 4 - группа 1, предмет 5 - группа 1, предмет 6 - группа 2; і т.д.

from django.core.management.base import BaseCommand
from django.utils import timezone

from django.contrib.auth.models import User
from dashboard.models import StudentGroups, TeachingAssignments, Subjects

from itertools import cycle

class Command(BaseCommand):
    help = 'Заповнення таблиці TeachingAssignments за допомогою Django ORM'  #python manage.py fill_db --help - виклик допомоги

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)

        teacher_ids = list(range(3, 11))
        subject_numbers = list(range(1, 24))
        group_numbers = list(range(1, 6))

        subjects_by_groups = {
            1: subject_numbers[:5],
            2: subject_numbers[5:10],
            3: subject_numbers[10:15],
            4: subject_numbers[15:19],
            5: subject_numbers[19:23]
        }

        for group_num, subjects in subjects_by_groups.items():
            teachers = cycle(teacher_ids)
            for subject in subjects:
                teacher_id = next(teachers)
                ta = TeachingAssignments.objects.create(
                    teacher_id=teacher_id,
                    subject_id=subject,
                    group_id=group_num
                )
                ta.save()
