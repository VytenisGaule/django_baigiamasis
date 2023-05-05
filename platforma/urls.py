from django.urls import path, include, re_path
from . import views


urlpatterns = [
    path('profile/', views.profilis, name='profile_endpoint'),
    path('distributors/', views.DistributorListView.as_view(), name='distributors_endpoint'),
    path('distributors/<int:distributor_id>', views.DistributorDetailView.as_view(), name='distributor_endpoint'),
    path('forwarders/', views.ForwarderListView.as_view(), name='forwarders_endpoint'),
    path('forwarders/<int:forwarder_id>', views.ForwarderDetailView.as_view(), name='forwarder_endpoint'),
    path('customers/', views.CustomerListView.as_view(), name='customers_endpoint'),
    path('customers/<int:forwarder_id>', views.CustomerDetailView.as_view(), name='customer_endpoint'),
    path('search/', views.search, name='search_endpoint'),
]

urlpatterns = urlpatterns + [
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name="register_endpoint"),
]

"""Customer views"""
urlpatterns = urlpatterns + [
    path('', views.ItemListView.as_view(), name='items_endpoint'),
    path('<int:pk>', views.ItemDetailView.as_view(), name='item_endpoint'),
    path('mycart/<int:customer_id>/', views.ShoppingCartView.as_view(), name='mycart_endpoint'),
    path('mycart/add/<int:distributor_id>/<int:item_id>/', views.AddToCartView.as_view(), name='add_to_cart_endpoint'),
    path('mycart/<int:customer_id>/<int:cart_id>/', views.ShoppingCartItemView.as_view(), name='cartitem_endpoint'),
    path('mycart/<int:customer_id>/<int:pk>/delivery/', views.ShoppingCartUpdateDeliveryView.as_view(), name='delivery_endpoint'),
    path('mycart/<int:customer_id>/<int:pk>/delete/', views.ShoppingCartDeleteView.as_view(), name='cart_delete_endpoint'),
    path('mycart/<int:customer_id>/<int:cart_id>/<int:pk>', views.ShoppingCartItemUpdateView.as_view(), name='update_cartitem_endpoint'),
]
