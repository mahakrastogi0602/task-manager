from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import TaskListCreateView

urlpatterns = [
    path('', views.task_list, name='task-list'),
    path('create/', views.task_create, name='task-create'),
    path('update/<int:pk>/', views.task_update, name='task-update'),
    path('delete/<int:pk>/', views.task_delete, name='task-delete'),

    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register_view, name='register'),
    path('today/', views.today_tasks, name='today-tasks'),
    path('lists/', views.task_lists, name='task-lists'),
    path('lists/<int:list_id>/', views.tasks_by_list, name='tasks-by-list'),
    path('lists/create/', views.tasklist_create, name='tasklist-create'),
    path('reminders/', views.task_reminders, name='task-reminders'),
    path('dashboard/', views.task_dashboard, name='task-dashboard'),
    path('', views.task_list_view, name='task-list'),
    path('lists/create/', TaskListCreateView.as_view(), name='create-tasklist'),
    path('calendar/', views.calendar_view, name='task-calendar'),
    path('calendar/events/', views.task_events, name='task-events'),
    path('export/csv/', views.export_tasks_csv, name='export-csv'),
    path('export/pdf/', views.export_tasks_pdf, name='export-pdf'),












]
