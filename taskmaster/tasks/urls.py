from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('home/', views.home, name='home'),
    path('notification-settings/', views.show_notification_settings, name='notification_settings'),
    path('save-notification-settings/', views.save_notification_settings, name='save_notification_settings'),
    path('mark-all-notifications-as-read/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add_project/', views.add_project, name='add_project'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('task/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('task/<int:task_id>/complete/', views.mark_task_completed, name='mark_task_completed'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/add_task/', views.add_task, name='add_task'),
    path('project/<int:project_id>/add_user/', views.add_user_to_project, name='add_user_to_project'),
    path('project/<int:project_id>/remove_user/<int:user_id>/', views.remove_user_from_project, name='remove_user_from_project'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/complete/', views.mark_project_completed, name='mark_project_completed'),
    # Другие URL-шаблоны проекта
]
