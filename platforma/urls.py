from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index_endpoint'),
    path('profilis/', views.profilis, name='profilis_endpoint'),
    path('distributors/', views.DistributorListView.as_view(), name='distributors_endpoint'),
    path('distributors/<int:author_id>', views.DistributorDetailView.as_view(), name='distributor_endpoint'),
]

urlpatterns = urlpatterns + [
    path("accounts/", include('django.contrib.auth.urls')),
    path("accounts/register/", views.register, name="register_endpoint"),
]
