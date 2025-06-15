# tasks/management/commands/send_reminders.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from tasks.models import Task
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Send reminders for tasks due today'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        tasks = Task.objects.filter(due_date=today, complete=False, reminder=True)

        for task in tasks:
            subject = f"⏰ Reminder: {task.title} is due today!"
            message = f"Hey {task.user.first_name or task.user.username},\n\nDon't forget your task:\n\n{task.title}\n\nDue today: {task.due_date}\n\n- Personal Task Manager"
            recipient = task.user.email

            if recipient:
                send_mail(
                    subject,
                    message,
                    'noreply@yourdomain.com',
                    [recipient],
                    fail_silently=False,
                )

        self.stdout.write(self.style.SUCCESS('Reminders sent successfully!'))
