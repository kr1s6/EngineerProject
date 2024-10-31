from django.urls import path

from . import views

urlpatterns = [
    path("index", views.home, name="home"),
    path("", views.home, name="home"),
    path("register/", views.UserRegisterView.as_view(), name="register_user"),
    path("login/", views.UserLoginView.as_view(), name="login"),  # TODO change to proper one later
    path("logout/", views.logout_view, name="logout")
]
