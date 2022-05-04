from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from rest_framework import viewsets

from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm
import logging
logger = logging.getLogger('cart')


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['update'])
    return redirect('cart:cart_detail')


# def cart_remove(request, product_id):
#     cart = Cart(request)
#     product = get_object_or_404(Product, id=product_id)
#     cart.remove(product)
#     messages.success(request, 'Удалено')
#     return redirect('cart:cart_detail')


# def cart_detail(request):
#     cart = Cart(request)
#     for item in cart:
#         item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'update': True})
#     return render(request, 'cart/detail.html', {'cart': cart})

class CartViewSetList(viewsets.ViewSet):

    def list(self, request):
        cart = Cart(request)
        logger.info("You came here to observe products in cart")
        for item in cart:
            item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'update': True})
        return render(request, 'cart/detail.html', {'cart': cart})


class CartViewSetDestroy(viewsets.ViewSet):
    def destroy(self, request, product_id=None):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        messages.success(request, 'Удалено')
        return redirect('cart:cart_detail')
