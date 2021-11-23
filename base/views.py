from django.http.response import HttpResponse
from django.shortcuts import render
from .models import Room

def home(request):
    rooms = Room.objects.all()
    data = {'rooms':rooms}
    return render(request, 'base/home.html', data)

def room(request, pk):
    room = Room.objects.get(id = pk)
    data = {'room':room}
    return render(request, 'base/room.html', data)