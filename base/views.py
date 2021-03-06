from django.db.models import Q
from django.contrib import messages
from django.db.models.query import EmptyQuerySet
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email= request.POST.get('email').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email= email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, 'Invalid Username or Password')

    data = {'page':page}
    return render(request, 'base/login_register.html', data)


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    page = 'register'
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        if User.objects.filter(username=request.POST.get('username').lower()).exists():
            messages.error(request, 'Username already Taken. Please choose a different username')
        if User.objects.filter(email=request.POST.get('email').lower()).exists():
            messages.error(request, 'Email already in use. Please choose a different email')    
        if request.POST.get('password1') != request.POST.get('password2'):
            messages.error(request, 'Passwords do not match.')
        else: 
            messages.error(request, 'Password must contain atleast one capital letter, one digit,one special character and must be atleast 8 charachters long')
    data = {'page':page, 'form':form}
    return render(request,'base/login_register.html', data)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
 
    topic = Topic.objects.all()[0:5]

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    room_count = rooms.count()
    activity_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    data = {'rooms':rooms, 'topics':topic, 'room_count':room_count, 'activity_messages': activity_messages}

    return render(request, 'base/home.html', data)

def room(request, pk):
    room = Room.objects.get(id = pk)
    room_messages = room.message_set.all().order_by('created')
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    data = {'room':room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'base/room.html', data)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    activity_messages = user.message_set.all()
    topic = Topic.objects.all()
    data = {'user': user, 'rooms': rooms, 'activity_messages': activity_messages, 'topics': topic}
    return render(request, 'base/profile.html', data)

@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host= request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')

    data = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', data)

@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed to update this room!')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        return redirect('home')

    data = {'form':form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', data)

@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed to delete this room!')
    if request.method == "POST":
        room.delete()
        return redirect('home')
        
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed to delete this message!')
    if request.method == "POST":
        message.delete()
        return redirect('home')
        
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='/login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    data = {'topics': topics}
    return render(request, 'base/topics.html', data)

def activitiesPage(request):
    room_messages = Message.objects.all()[0:3]
    return render(request, 'base/activity.html', {'room_messages': room_messages})