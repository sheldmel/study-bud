from django.http.response import HttpResponse
from django.shortcuts import render


rooms = [
    {'id':1, 'name': 'Lets learn python'},
    {'id':2, 'name': 'Design with me'},
    {'id':3, 'name': 'Frontend dev'},
]

def home(request):
    data = {'rooms':rooms}
    return render(request, 'base/home.html', data)

def room(request, pk):
    room = None
    for i in rooms:
        if i['id'] == int(pk):
            room = i
    data = {'room':room}
    return render(request, 'base/room.html', data)