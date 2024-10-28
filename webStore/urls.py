from django.urls import path

from . import views

urlpatterns = [
    path("index", views.home, name="home"),
    path("", views.home, name="home"),
    path("register/", views.register_user, name="register_user"),
    path("login/", views.home, name="login") # TODO change to proper one later
]
