from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Thread, Reply

def home(request):
    return render(request, 'forum/home.html')

def thread(request):
    thread_id = request.GET.get("id")
    thread = Thread.objects.filter(id=thread_id)
    print(thread.title)

    # TODO GET for thread
    return render(request, 'forum/thread.html')