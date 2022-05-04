from django.urls import path

from .views import (
    cart_add,
    # cart_detail,
    # cart_remove,
    CartViewSetList,
    CartViewSetDestroy
)

app_name = 'cart'

urlpatterns = [
    path('', CartViewSetList.as_view({'get': 'list'}), name='cart_detail'),
    # path('', cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', cart_add, name='cart_add'),
    # path('remove/<int:product_id>/', cart_remove, name='cart_remove'),
    path('remove/<int:product_id>/', CartViewSetDestroy.as_view({'get': 'destroy'}), name='cart_remove')
]
