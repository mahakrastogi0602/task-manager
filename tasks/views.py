from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Task, TaskList
from .forms import TaskForm, TaskListForm
from datetime import timedelta
from django.shortcuts import render
from .models import Task
from .forms import TaskForm
from datetime import date
from django.utils.timezone import now
from django.db.models import Count
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import csv
from django.http import HttpResponse
# Create your views here.
@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    # Sorting
    sort_by = request.GET.get('sort', '')
    if sort_by == 'due_asc':
        tasks = tasks.order_by('due_date')
    elif sort_by == 'due_desc':
        tasks = tasks.order_by('-due_date')
    elif sort_by == 'priority':
        tasks = tasks.order_by('priority')
    elif sort_by == 'frequency':
        tasks = tasks.order_by('recur_frequency')

    # Filtering
    filter_status = request.GET.get('status')
    if filter_status == 'completed':
        tasks = tasks.filter(complete=True)
    elif filter_status == 'incomplete':
        tasks = tasks.filter(complete=False)

    recur_filter = request.GET.get('recur')
    if recur_filter:
        tasks = tasks.filter(recur_frequency=recur_filter)

    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def task_create(request):
    form = TaskForm()
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user 
            task.save() 
            return redirect('task-list')

    return render(request, 'tasks/task_form.html', {'form': form})

from datetime import timedelta

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    form = TaskForm(instance=task)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save()

            # ✅ Recurrence logic
            if updated_task.complete and updated_task.recur_frequency != 'N' and updated_task.due_date:
                next_due = updated_task.due_date

                if updated_task.recur_frequency == 'D':
                    next_due += timedelta(days=1)
                elif updated_task.recur_frequency == 'W':
                    next_due += timedelta(weeks=1)
                elif updated_task.recur_frequency == 'M':
                    next_due = next_due.replace(
                        month=next_due.month % 12 + 1 if next_due.month < 12 else 1,
                        year=next_due.year if next_due.month < 12 else next_due.year + 1
                    )
                elif updated_task.recur_frequency == 'Y':
                    next_due = next_due.replace(year=next_due.year + 1)

                # Clone the task as a new one
                updated_task.pk = None
                updated_task.due_date = next_due
                updated_task.complete = False
                updated_task.save()

            return redirect('task-list')

    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task-list')
    return render(request, 'tasks/task_delete.html', {'task': task})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('task-list')
    
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log the user in after registration
            return redirect('task-list')
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def today_tasks(request):
    today = date.today()
    tasks = Task.objects.filter(user=request.user, due_date=today)
    return render(request, 'tasks/today_tasks.html', {'tasks': tasks})

@login_required
def task_lists(request):
    lists = TaskList.objects.filter(user=request.user)
    return render(request, 'tasks/task_lists.html', {'lists': lists})

@login_required
def tasklist_create(request):
    form = TaskListForm()
    if request.method == 'POST':
        form = TaskListForm(request.POST)
        if form.is_valid():
            tasklist = form.save(commit=False)
            tasklist.user = request.user
            tasklist.save()
            return redirect('task-lists')
    return render(request, 'tasks/tasklist_form.html', {'form': form})

@login_required
def tasks_by_list(request, list_id):
    task_list = get_object_or_404(TaskList, id=list_id, user=request.user)
    tasks = Task.objects.filter(task_list=task_list)

    return render(request, 'tasks/tasks_by_list.html', {
        'task_list': task_list,
        'tasks': tasks
    })

@login_required
def task_reminders(request):
    today = date.today()
    weekday = today.weekday()  # Monday=0, Sunday=6

    tasks = Task.objects.filter(user=request.user)

    reminders = []

    for task in tasks:
        if task.due_date == today:
            reminders.append(task)
        elif task.recur_frequency == 'D':
            reminders.append(task)
        elif task.recur_frequency == 'W' and task.due_date and task.due_date.weekday() == weekday:
            reminders.append(task)
        elif task.recur_frequency == 'M' and task.due_date and task.due_date.day == today.day:
            reminders.append(task)
        elif task.recur_frequency == 'Y' and task.due_date and task.due_date.month == today.month and task.due_date.day == today.day:
            reminders.append(task)

    return render(request, 'tasks/reminders.html', {'reminders': reminders})

def task_dashboard(request):

    
    tasks = Task.objects.filter(user=request.user)

    filter_type = request.GET.get('filter')
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    if filter_type == 'week':
        tasks = tasks.filter(due_date__range=[start_of_week, end_of_week])
    elif filter_type == 'completed':
        tasks = tasks.filter(complete=True)
    elif filter_type == 'incomplete':
        tasks = tasks.filter(complete=False)
    
    status_data = tasks.values('complete').annotate(count=Count('id'))
    freq_data = tasks.values('recur_frequency').annotate(count=Count('id'))
    priority_data = tasks.values('priority').annotate(count=Count('id'))

    # Completion Status
    status_data = tasks.values('complete').annotate(count=Count('id'))

    # Recurrence Frequency
    freq_data = tasks.values('recur_frequency').annotate(count=Count('id'))

    # Priority
    priority_data = tasks.values('priority').annotate(count=Count('id'))

    return render(request, 'tasks/dashboard.html', {
        'status_data': status_data,
        'freq_data': freq_data,
        'priority_data': priority_data,
        'filter_type': filter_type, 
    })

def task_list_view(request):
    tasks = Task.objects.filter(user=request.user)
    task_lists = TaskList.objects.filter(user=request.user)
    context = {
        'tasks': tasks, 
    }
    return render(request, 'tasks/task_list.html', context)

class TaskListCreateView(CreateView):
    model = TaskList
    fields = ['name']
    template_name = 'tasks/tasklist_form.html'
    success_url = reverse_lazy('task-list')  # or wherever you want to redirect

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

def calendar_view(request):
    return render(request, 'tasks/calendar.html')

@csrf_exempt
def task_events(request):
    tasks = Task.objects.filter(user=request.user).exclude(due_date__isnull=True)
    events = []
    for task in tasks:
        if task.due_date:
            events.append({
                'title': task.title,
                'start': task.due_date.isoformat(),
                'color': '#28a745' if task.complete else '#ffc107'
            })
    return JsonResponse(events, safe=False)

def export_tasks_csv(request):
    tasks = Task.objects.filter(user=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tasks.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Description', 'Due Date', 'Priority', 'Complete', 'Recurrence'])

    for task in tasks:
        writer.writerow([
            task.title,
            task.description,
            task.due_date,
            task.get_priority_display(),
            'Yes' if task.complete else 'No',
            task.get_recur_frequency_display(),
        ])

    return response

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def export_tasks_pdf(request):
    tasks = Task.objects.filter(user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tasks.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Your Tasks")
    p.setFont("Helvetica", 12)

    y -= 30

    for task in tasks:
        if y < 50:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 12)

        p.drawString(50, y, f"• {task.title} | Due: {task.due_date or 'N/A'} | "
                            f"Priority: {task.get_priority_display()} | "
                            f"Status: {'✅' if task.complete else '❌'}")
        y -= 20

    p.save()
    return response
