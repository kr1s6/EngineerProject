from django.urls import path

from . import views

urlpatterns = [
    path("index", views.home, name="home"),
    path("", views.home, name="home"),
    path("register/", views.UserRegisterView.as_view(), name="register_user"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("add_address/", views.UserAddressCreationView.as_view(), name="add_address"),
    path("add_category/", views.ProductCategoryCreationView.as_view(), name="add_category"),
    path("add_product/", views.ProductCreationView.as_view(), name="add_product"),
]