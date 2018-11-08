from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="forum-home"),
    path('thread/', views.thread, name="forum-thread"),
    path('login/', views.login, name="forum-login"),
    path('logout/', views.logout_view, name="forum-logout"),
    path('newthread/', views.new_thread, name="forum-new-thread"),
    path('newreply/', views.new_reply, name="forum-new-reply")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)