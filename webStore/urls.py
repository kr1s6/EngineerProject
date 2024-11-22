from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import HomeProductsListView

urlpatterns = [
    path("index", HomeProductsListView.as_view(), name='home'),
    path("", HomeProductsListView.as_view(), name="home"),
    path("register/", views.UserRegisterView.as_view(), name="register_user"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("add_address/", views.UserAddressCreationView.as_view(), name="add_address"),
    path("add_category/", views.ProductCategoryCreationView.as_view(), name="add_category"),
    path("add_product/", views.ProductCreationView.as_view(), name="add_product"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
