from django.http.response import HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import Room, Topic
from .forms import RoomForm

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

def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    data = {'form': form}
    return render(request, 'base/room_form.html', data)

def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance=room)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    data = {'form':form}
    return render(request, 'base/room_form.html', data)

def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect('home')
        
    return render(request, 'base/delete.html', {'obj': room})