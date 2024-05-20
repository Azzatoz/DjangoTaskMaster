from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('', views.home, name='home'),
    path('add_project/', views.add_project, name='add_project'),
    # Другие URL-шаблоны проекта
]
