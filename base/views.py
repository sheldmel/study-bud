from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Room, Topic
from .forms import RoomForm

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username= request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username = username, password=password)

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
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured. Please try again')
    data = {'page':page, 'form':form}
    return render(request,'base/login_register.html', data)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
 
    topic = Topic.objects.all()

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    room_count = rooms.count()
    data = {'rooms':rooms, 'topics':topic, 'room_count':room_count}

    return render(request, 'base/home.html', data)

def room(request, pk):
    room = Room.objects.get(id = pk)
    data = {'room':room}
    return render(request, 'base/room.html', data)

@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    data = {'form': form}
    return render(request, 'base/room_form.html', data)

@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('Your are not allowed to update this room!')
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    data = {'form':form}
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