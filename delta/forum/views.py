from django.shortcuts import render

def home(request):
    return render(request, 'forum/home.html')

def thread(request):
    # TODO GET for thread
    return render(request, 'forum/thread.html')