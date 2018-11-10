from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from .models import Thread, Reply, Subforum
from .forms import LoginForm, ThreadForm, ReplyForm


def login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            request.session['user_id'] = user.id
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
        # Get subforum request
        sub = request.GET.get('sub')
        if sub:
            # Load posts of subforum
            try: 
                subforum = Subforum.objects.get(id=sub) 
                context['subforum'] = subforum.__dict__
                threads = subforum.thread_set.all()
                context['threads'] = threads
                context['threadform'] = ThreadForm()
                return render(request, 'forum/home.html', context)
            except ObjectDoesNotExist:
                return redirect('forum-home')
        else:
            # Load subforums
            context['subforums'] = {}
            for subforum in Subforum.objects.all():
                try:
                    context['subforums'][subforum.category][subforum.id] = subforum.__dict__
                except KeyError:
                    context['subforums'][subforum.category] = {}
                    context['subforums'][subforum.category][subforum.id] = subforum.__dict__
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
        # Load ReplyForm into context
        context['replyform'] = ReplyForm()

        # Load thread into context if it exists
        context['thread'] = thread.__dict__

        # Load author into context 
        author = User.objects.get(id=context['thread']['author_id'])
        context['thread']['author'] = author.__dict__
        context['thread']['author']['titles'] = author.usertitle_set.all()
        context['thread']['author']['stats'] = {
            'Total Posts': author.thread_set.count()+author.reply_set.count()
        }

        # Load replies into context
        context['thread']['replies'] = {}

        for reply in thread.reply_set.all():
            context['thread']['replies'][reply.id] = reply.__dict__

        # Load author into replies
        for reply in thread.reply_set.all():
            replier = User.objects.get(id=context['thread']['replies'][reply.id]['author_id'])
            context['thread']['replies'][reply.id]['author'] = replier.__dict__
            context['thread']['replies'][reply.id]['author']['titles'] = replier.usertitle_set.all()
            context['thread']['replies'][reply.id]['author']['stats'] = {
                'Total Posts': replier.thread_set.count()+author.reply_set.count()
            }

    except ObjectDoesNotExist: 
        add_error(request, 'NoThreadFound')
        return redirect('forum-home')

    # Get session stuff
    context['user'] = {
        'id': request.session.get('user_id')
    }
        
    return render(request, 'forum/thread.html', context)    


def new_thread(request):
    if request.POST:
        subforum = request.GET.get('sub')
        thread = ThreadForm(request.POST)
        if thread.is_valid():
            thread = thread.save(commit=False)
            thread.author = User.objects.get(id=request.session['user_id'])
            thread.subforum = Subforum.objects.get(id=subforum) 
            thread.save()
            # Redirect to original sub
            response = redirect('forum-home')
            response['Location'] += '?sub=' + subforum 
            return response
    return redirect('forum-home')
    
def new_reply(request):
    if request.POST:
        thread = request.GET.get('id')
        reply = ReplyForm(request.POST)
        if reply.is_valid():
            reply = reply.save(commit=False)
            reply.author = User.objects.get(id=request.session['user_id'])
            reply.thread = Thread.objects.get(id=thread)
            reply.save()
            # Redirect to original thread
            response = redirect('forum-thread')
            response['Location'] += '?id=' + thread
            return response
    return redirect('forum-home')


def check_login(request):
    if request.session.get('user_id') is not None:
        return True
    return False


def add_error(request, error_type):
    try:
        if error_type == 'NoThreadFound':
            request.session['errors']['NoThreadFoundError'] = {
                'type': 'warning',
                'content': 'Error: Thread not found.'
            }
    except KeyError:
        request.session['errors'] = {}
        add_error(request, error_type)


def load_errors_context(request, context):
    context['errors'] = {}
    try:
        for key, error in request.session['errors'].items():
            context['errors'].update({
                key: {
                    'type': error['type'],
                    'content': error['content']
                }
            })
        request.session['errors'] = {}
    except KeyError:
        return
