from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.

# *rooms = [
# *   {"id": 1, "name": "Lets learn python"},
# *    {"id": 2, "name": "Design with me"},
# *    {"id": 3, "name": "Frontend development"},
# *]


def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(host__username__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
        | Q(room__name__icontains=q)
        | Q(user__username__icontains=q)
    )
    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
    }
    return render(request, "base/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()  # type: ignore
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            room=room,
            user=request.user,
            body=request.POST.get("body"),
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)  # type: ignore
    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }
    return render(request, "base/room.html", context)


def userProfile(request, pk):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    user = User.objects.get(id=pk)
    rooms = user.room_set.filter(topic__name__icontains=q)  # type: ignore
    room_messages = user.message_set.filter(  # type: ignore
        Q(room__topic__name__icontains=q)
        | Q(room__name__icontains=q)
        | Q(user__username__icontains=q)
    )
    t = []
    for n in user.room_set.all():  # type: ignore
        if n.topic.name not in t:
            t.append(n.topic.name)
    room_topics_count = len(t)
    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "room_topics_count": room_topics_count,
        "room_topics_names": t,
    }
    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=int(pk))
    room = message.room
    homePath = "http://" + request.META["HTTP_HOST"] + "/"
    roomPath = homePath + "room/" + str(room.id) + "/"  # type: ignore
    profilePath = homePath + "profile/" + str(request.user.id) + "/"  # type: ignore
    refererPath = request.META.get("HTTP_REFERER")
    pathId = 3
    if refererPath == roomPath:
        pathId = 2
    elif refererPath == profilePath:
        pathId = 1
    elif refererPath == homePath:
        pathId = 3

    context = {
        "obj": message,
        "class_name": "message",
        "pathId": pathId,
    }
    return render(request, "base/delete.html", context)


@login_required(login_url="login")
def processing_delete(request, obj_id, path_id, class_name):
    if class_name == "message":
        message = Message.objects.get(id=int(obj_id))
        room = message.room
        countOfMessages = len(Message.objects.filter(user=message.user))
        path_id = int(path_id)
        if request.method == "POST":
            if countOfMessages == 1:
                message.room.participants.remove(message.user)
            message.delete()
            if path_id == 1:
                return redirect("user-profile", request.user.id)
            elif path_id == 2:
                return redirect("room", room.id)  # type: ignore
            else:
                return redirect("home")
    if class_name == "room":
        room = Room.objects.get(id=obj_id)
        if request.method == "POST":
            room.delete()
            return redirect("home")
    return render(request, "base/delete.html", {})


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            host=request.user,
        )
        return redirect("home")
    context = {"form": form, "topics": topics}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=int(pk))
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")
    context = {"form": form, "topics": topics, "room": room}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    return render(
        request, "base/delete.html", {"obj": room, "class_name": "room", "pathId": 3}
    )


def loginPage(request):
    page = "loginPage"
    if request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method == "POST":
            username = request.POST.get("username").lower()
            password = request.POST.get("password")
            try:
                user = User.objects.get(username=username)
            except:
                messages.error(request, "Invalid username or password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password")
        context = {"page": page}
        return render(request, "base/login_register.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", user.id)
        else:
            messages.error(request, "Something went wrong")
    context = {"form": form}
    return render(request, "base/update_user.html", context)


def registerPage(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            username = username.lower()
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Something went wrong")
    context = {"form": form}
    return render(request, "base/login_register.html", context)


def topicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, "base/topics.html", {"topics": topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, "base/activity.html", {"room_messages": room_messages})
