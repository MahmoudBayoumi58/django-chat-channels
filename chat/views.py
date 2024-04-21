from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from chat.models import Room, Message


# Create your views here.
@login_required
def room(request, slug):
    """ Details group per chat """
    room = Room.objects.get(slug=slug)
    messages = Message.objects.filter(room=room)[0:30]
    return render(request, 'chat/room.html', {'room': room, 'messages': messages})
