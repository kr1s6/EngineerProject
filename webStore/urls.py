from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import rate_product
from .consumers import ChatConsumer
urlpatterns = [
    path("index", views.HomePageView.as_view(), name='home'),
    path("", views.HomePageView.as_view(), name="home"),
    path("all_products/", views.AllProductsView.as_view(), name="all_products"),
    path('search/', views.ProductSearchView.as_view(), name='search'),
    path("register/", views.UserRegisterView.as_view(), name="register_user"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('add_address/', views.UserAddressCreationView.as_view(), name='add_address'),
    path("address-selection/", views.AddressSelectionView.as_view(), name="address_selection"),
    path('payment/', views.PaymentMethodView.as_view(), name='payment_form'),
    path('blik-payment/', views.BlikCodeView.as_view(), name='blik_code'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('create-order/', views.OrderCreateView.as_view(), name='create_order'),
    path('order-status/<int:order_id>/', views.get_order_status, name='order_status'),
    path('rate/<int:product_id>/', rate_product, name='rate_product'),
    path('rate/<int:product_id>/<int:rating_id>/', rate_product, name='edit_rate'),
    # chat / messages endpoints
    path('messages/', views.MessagesListView.as_view(), name='messages_list'),  # Lista konwersacji z przekierowaniem
    path('messages/send/', views.send_message, name='send_message'),  # Wysyłanie wiadomości
    path('messages/<int:conversation_id>/load/', views.load_messages, name='load_messages'),
    # Pobieranie nowych wiadomości
    path('messages/<int:conversation_id>/save-last-opened/', views.save_last_opened_conversation, name='save_last_opened'),
    path('messages/<int:conversation_id>/fetch-new/', views.fetch_new_messages, name='fetch_new_messages'),
    path('product-like/<int:product_id>/', views.product_like, name="product_like"),
    path('favorites/', views.FavoritesListView.as_view(), name='favorites'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:product_id>/ratings/', views.get_ratings_html, name='get_ratings_html'),
    path('category/<int:category_id>/products/', views.CategoryProductsView.as_view(), name='category_products'),
    path('add-to-cart/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('update-cart-item/<int:product_id>/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
    path('update-cart-item/<int:product_id>/<int:quantity>/', views.UpdateCartItemView.as_view(),
         name='update_cart_item_with_quantity'),
    path('cart/', views.CartDetailView.as_view(), name='cart_detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
