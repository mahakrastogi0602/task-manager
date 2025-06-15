from django import forms
from .models import Task, TaskList

class TaskForm(forms.ModelForm):
    
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), required=False
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'complete', 'due_date', 'priority', 'task_list','recur_frequency','task_list']

class TaskListForm(forms.ModelForm):
    class Meta:
        model = TaskList
        fields = ['name']
    