from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import Thread, Reply
from .forms import LoginForm

def check_login(request):
    if request.session.get('user_id') is not None:
        return True
    return False

def login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            print("Logged in as " + username)
            request.session['user_id'] = user.id
        else:
            print('Login failed')
        return redirect('forum-home')

def logout_view(request):
    logout(request)
    return redirect('forum-home')

def home(request):
    context = {}
    # Load error messages
    load_errors_context(request, context)

    if check_login(request) is False: 
        context['login'] = LoginForm()
        return render(request, 'forum/splash.html', context)
    else:
        # Get session stuff
        context['user'] = {
            'id': request.session.get('user_id')
        }
        return render(request, 'forum/home.html', context)

def thread(request):
    if check_login(request) is False: 
        return redirect('forum-home')

    # Init thread context as blank dictionary
    context = {}
    # Load error messages
    load_errors_context(request, context)
    # Get Thread from GET request
    thread_id = request.GET.get("id")
    # Check if user actually requested a specific thread 
    if thread_id == None:
        return redirect('forum-home')
    # Check if thread requested exists
    try:
        thread = Thread.objects.get(id=thread_id)
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
    except ObjectDoesNotExist: 
        add_error(request, 'NoThreadFound')
        return redirect('forum-home') # TODO redirect to home page with NoThreadFound error msg

    # Get session stuff
    context['user'] = {
        'id': request.session.get('user_id')
    }
        
    return render(request, 'forum/thread.html', context)

def add_error(request, error_type):
    try:
        if error_type == 'NoThreadFound':
            request.session['errors']['NoThreadFoundError'] = {
                'type': 'warning',
                'content': '<strong>Error.</strong> Thread not found'
            }
    except KeyError:
        request.session['errors'] = {}
        add_error(request, error_type)


def load_errors_context(request, context):
    context['errors'] = {}
    try:
        print(request.session['errors'])
        for key, error in request.session['errors'].items():
            context['errors'].update({
                key: {
                    'type': error['type'],
                    'content': error['content']
                }
            })
            request.session['errors'].pop(key, None)
    except KeyError:
        return

