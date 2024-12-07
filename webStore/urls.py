from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import HomeProductsListView, FavoritesListView, ProductCreationView

urlpatterns = [
    path("index", HomeProductsListView.as_view(), name='home'),
    path("", HomeProductsListView.as_view(), name="home"),
    path('search/', views.ProductSearchView.as_view(), name='search'),
    path("register/", views.UserRegisterView.as_view(), name="register_user"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("add_address/", views.UserAddressCreationView.as_view(), name="add_address"),
    path("add_category/", views.ProductCategoryCreationView.as_view(), name="add_category"),
    path("add_product/", ProductCreationView.as_view(), name="add_product"),
    path('product-like/<int:product_id>/', views.product_like, name="product_like"),
    path('favorites/', FavoritesListView.as_view(), name='favorites'),
    path('product/<int:id>/', views.product_detail, name='product_detail')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
