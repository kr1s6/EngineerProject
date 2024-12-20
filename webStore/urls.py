from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
urlpatterns = [
    path("index", views.HomePageView.as_view(), name='home'),
    path("", views.HomePageView.as_view(), name="home"),
    path("all_products/", views.AllProductsView.as_view(), name="all_products"),
    path('search/', views.ProductSearchView.as_view(), name='search'),
    path("register/", views.UserRegisterView.as_view(), name="register_user"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('add_address/', views.UserAddressCreationView.as_view(), name='add_address'),
    path('payment/', views.PaymentMethodView.as_view(), name='payment_form'),
    path('product-like/<int:product_id>/', views.product_like, name="product_like"),
    path('favorites/', views.FavoritesListView.as_view(), name='favorites'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<int:category_id>/products/', views.CategoryProductsView.as_view(), name='category_products'),
    path('add-to-cart/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('update-cart-item/<int:product_id>/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
    path('update-cart-item/<int:product_id>/<int:quantity>/', views.UpdateCartItemView.as_view(), name='update_cart_item_with_quantity'),
    path('cart/', views.CartDetailView.as_view(), name='cart_detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
