from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="forum-home"),
    path('thread/', views.thread, name="forum-thread")
]