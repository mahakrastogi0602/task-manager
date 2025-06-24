from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class TaskList(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    
class Task(models.Model):
     
    PRIORITY_CHOICES = [
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, null=True, blank=True)
    

    RECUR_FREQUENCY_CHOICES = [
        ('N', 'None'),
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
        ('Y', 'Yearly'),
    ]
    recur_frequency = models.CharField(
        max_length=1,
        choices=RECUR_FREQUENCY_CHOICES,
        default='N'
    )

    def __str__(self):
        return self.title
    

    
