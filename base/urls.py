from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("room/<str:pk>/", views.room, name="room"),
    path("create-room/", views.createRoom, name="create-room"),
    path("update-room/<str:pk>", views.updateRoom, name="update-room"),
    path("delete-room/<str:pk>", views.deleteRoom, name="delete-room"),
    path("login/", views.loginPage, name="login"),
    path("register/", views.registerPage, name="register"),
    path("logout/", views.logoutUser, name="logout"),
    path("delete-message/<str:pk>/", views.deleteMessage, name="delete-message"),
    path(
        "processing-delete/<str:obj_id>/<str:path_id>/<str:class_name>",
        views.processing_delete,
        name="processing-delete",
    ),
    path("profile/<str:pk>/", views.userProfile, name="user-profile"),
    path("update-user/", views.updateUser, name="update-user"),
    path("topics/", views.topicsPage, name="topics"),
    path("activity/", views.activityPage, name="activity"),
]
