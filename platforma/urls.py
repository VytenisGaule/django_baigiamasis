from django.urls import path, include, re_path
from . import views


"""admin views - statistics"""
urlpatterns = [
    path('distributors/', views.DistributorListView.as_view(), name='distributors_endpoint'),
    path('distributors/<int:distributor_id>', views.DistributorDetailView.as_view(), name='distributor_endpoint'),
    path('forwarders/', views.ForwarderListView.as_view(), name='forwarders_endpoint'),
    path('forwarders/<int:forwarder_id>', views.ForwarderDetailView.as_view(), name='forwarder_endpoint'),
    path('customers/', views.CustomerListView.as_view(), name='customers_endpoint'),
    path('customers/<int:forwarder_id>', views.CustomerDetailView.as_view(), name='customer_endpoint'),
]

"""common views"""
urlpatterns = urlpatterns + [
    path('locations/', views.ShipmentLocationsView.as_view(), name='locations_endpoint'),
    path('shipments/<str:location>/', views.ShipmentsAtLocationView.as_view(), name='shipment_status_endpoint'),
    path('shipments/<int:distributor_id>/<int:customer_id>/<int:forwarder_id>/<int:pk>/',
         views.ShipmentDetailView.as_view(), name='shipment_endpoint'),
    path('search/', views.search, name='search_endpoint'),
    path('profile/', views.profilis, name='profile_endpoint'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name="register_endpoint"),
]

"""Customer views"""
urlpatterns = urlpatterns + [
    path('', views.ItemListView.as_view(),
         name='items_endpoint'),
    path('<int:pk>', views.ItemDetailView.as_view(),
         name='item_endpoint'),
    path('mycart/<int:customer_id>/', views.ShoppingCartView.as_view(),
         name='mycart_endpoint'),
    path('mycart/add/<int:distributor_id>/<int:item_id>/', views.AddToCartView.as_view(),
         name='add_to_cart_endpoint'),
    path('mycart/<int:customer_id>/<int:cart_id>/', views.ShoppingCartItemView.as_view(),
         name='cartitem_endpoint'),
    path('mycart/<int:customer_id>/<int:pk>/delivery/', views.ShoppingCartUpdateDeliveryView.as_view(),
         name='delivery_endpoint'),
    path('mycart/<int:customer_id>/<int:pk>/delete/', views.ShoppingCartDeleteView.as_view(),
         name='cart_delete_endpoint'),
    path('mycart/<int:customer_id>/purchase/', views.PurchaseAndPayView.as_view(),
         name='purchase_cart_endpoint'),
    path('mycart/<int:customer_id>/<int:cart_id>/<int:pk>', views.ShoppingCartItemUpdateView.as_view(),
         name='update_cartitem_endpoint'),
]

"""Distributor views"""
urlpatterns = urlpatterns + [
    path('myitems/<int:distributor_id>/', views.ItemByDistributorListView.as_view(),
         name='distributor_items_endpoint'),
    path('myitems/<int:distributor_id>/new', views.ItemByDistributorCreate.as_view(),
         name='distributor_new_item_endpoint'),
    path('myitems/<int:distributor_id>/<int:pk>/edit', views.ItemByDistributorUpdate.as_view(),
         name='distributor_edit_item_endpoint'),
    path('myitems/<int:distributor_id>/<int:pk>/delete', views.ItemByDistributorDelete.as_view(),
         name='distributor_delete_item_endpoint'),
    path('myitems/<int:distributor_id>/<int:pk>/', views.ItemByDistributorView.as_view(),
         name='distributor_item_endpoint'),
]

"""Forwarder views"""
urlpatterns = urlpatterns + [
    path('myshipments/<int:forwarder_id>/', views.ShipmentsByForwarderListView.as_view(),
         name='forwarder_shipments_endpoint'),
]
