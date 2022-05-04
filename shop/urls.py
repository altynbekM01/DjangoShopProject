from django.contrib import admin
from django.urls import path
from . import views

from shop.views import (
    product_list,
    product_detail, RegistrationAPIView, LoginAPIView, UserRetrieveUpdateAPIView, brand_list, man_woman_list
)

app_name = 'shop'

urlpatterns = [
    path('', product_list, name='product_list'),
    path('api/user/', UserRetrieveUpdateAPIView.as_view()),
    path('api/users/', RegistrationAPIView.as_view()),
    path('api/users/login/', LoginAPIView.as_view()),
    path('api/show', views.home2),
    path('add_product', views.add_product , name = 'add_product'),
    path('api/add_brand', views.BrandCreateView.as_view()),
    path('api/add_gender', views.GenderCreateView.as_view()),
    path('<str:category_slug>/', product_list, name='product_list_by_category'),
    path('<str:brand_slug>', brand_list, name='brands_views'),
    # path('<about>/', about, name='about'),
    path('<str:gender_slug>//', man_woman_list, name='gender_views'),
    path('<int:id>/<str:slug>/', product_detail, name='product_detail')
]
