from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Thread, Reply

def check_login(request):
    if request.session.get('user_id') is not None:
        return True
    print("Redirecting")
    return False

def home(request):
    if check_login(request) is False: 
        return render(request, 'forum/splash.html')
    else:
        return render(request, 'forum/home.html')

def thread(request):
    if check_login(request) is False: 
        return redirect('forum-home')

    # Init context as blank dictionary
    context = {}
    # Get Thread from GET request
    thread_id = request.GET.get("id")
    # Check if user actually requested a specific thread 
    if thread_id == None:
        return render(request, 'forum/thread.html') # TODO redirect to home page
    thread = Thread.objects.get(id=thread_id)
    # Check if thread requested exists
    if thread:
        # Load thread into context if it exists
        context['thread'] = thread.__dict__
        # Load author into context 
        context['thread']['author'] = User.objects.get(id=context['thread']['author_id']).__dict__
        # Load replies into context
        context['thread']['replies'] = {}
        for reply in thread.reply_set.all():
            context['thread']['replies'][reply.id] = reply.__dict__
        # Load author into replies
        for reply in thread.reply_set.all():
            context['thread']['replies'][reply.id]['author'] =  User.objects.get(id=context['thread']['replies'][reply.id]['author_id']).__dict__
    else: 
        return render(request, 'forum/thread.html') # TODO redirect to home page with NoThreadFound error msg
        
    return render(request, 'forum/thread.html', context)