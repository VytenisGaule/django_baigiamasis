from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index_endpoint'),
    path('profile/', views.profilis, name='profile_endpoint'),
    path('distributors/', views.DistributorListView.as_view(), name='distributors_endpoint'),
    path('distributors/<int:distributor_id>', views.DistributorDetailView.as_view(), name='distributor_endpoint'),
    path('forwarders/', views.ForwarderListView.as_view(), name='forwarders_endpoint'),
    path('forwarders/<int:forwarder_id>', views.ForwarderDetailView.as_view(), name='forwarder_endpoint'),
    path('customers/', views.CustomerListView.as_view(), name='customers_endpoint'),
    path('customers/<int:forwarder_id>', views.CustomerDetailView.as_view(), name='customer_endpoint'),
]

urlpatterns = urlpatterns + [
    path("accounts/", include('django.contrib.auth.urls')),
    path("accounts/register/", views.register, name="register_endpoint"),
]
