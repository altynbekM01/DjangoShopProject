
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.utils import json
from datetime import datetime, date

from .models import Category, Product, Brand, Gender
from cart.forms import CartAddProductForm
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .renderers import UserJSONRenderer
from .serializers import LoginSerializer, RegistrationSerializer, UserSerializer, BrandSerializer, GenderSerializer
from shop.serializers import ProductSerializer
import logging

from django.views.generic import (
    ListView,
    DetailView
)
'''
class ProductListView(ListView):
    template_name = 'shop/product/list.html'
    queryset = Product.objects.all()
    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        return context
'''

logger = logging.getLogger('shop')



def product_list(request, category_slug=None):
    logger.info("You came here to observe the list")
    category = None
    categories = Category.objects.all()
    brands = Brand.objects.all()
    genders = Gender.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'brands':brands,
        'genders': genders,
    }
    return render(request, 'shop/product/list.html', context)

def brand_list(request, brand_slug=None):
    logger.info("You came here to observe the list")
    category = None
    brand = None
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.filter(available=True)
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = Product.objects.filter(brand=brand)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'brands': brands
    }
    return render(request, 'shop/product/list.html', context)

def man_woman_list(request, gender_slug=None):
    category = None
    gender = None
    categories = Category.objects.all()
    genders = Gender.objects.all()
    products = Product.objects.filter(available=True)
    if gender_slug:
        gender = get_object_or_404(Gender, slug=gender_slug)
        products = Product.objects.filter(gender=gender)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'genders': genders,

    }
    return render(request, 'shop/product/list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    context = {
        'product': product,
        'cart_product_form': cart_product_form
    }
    return render(request, 'shop/product/detail.html', context)

# def about(request):
#
#     return render(request, 'shop/about.html')

@csrf_exempt
def home2(request):
    product_list = Product.objects.all().order_by("-created_at")
    # return render(request, 'main/index.html', {"todo_items": todo_items_list})
    # return render(request, 'main/tester.html')
    # return render(request, 'main/index.html', {"todo_items": todo_items_list})
    if request.method == 'GET':
        product_list = Product.objects.all().order_by("-created_at")
        serializer = ProductSerializer(product_list, many=True)
        # return Response(serializer.data)
        # return render(request, 'main/index.html', {"todo_items": todo_items_list})
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            # serializer.save()
            return JsonResponse(serializer.data, safe=False)
        return JsonResponse(serializer.errors, safe=False, status=400)

@csrf_exempt
def add_product(request):
    print(request.POST)
    category  = request.POST["category"]
    brand  = request.POST["brand"]
    gender = request.POST["gender"]
    name  = request.POST["name"]
    slug = request.POST["slug"]
    description = request.POST["description"]
    price = request.POST["price"]
    available =  request.POST["available"]
    stock = request.POST["stock"]
    created_at = datetime.today()
    updated_at = datetime.today()
    image = request.POST["image"]
    created_object = Product.objects.create(category=category, brand=brand, gender=gender, name=name, slug=slug,description=description,price=price,available=available,stock=stock, created_at=created_at, updated_at=updated_at, image=image)
    # lengthOfToDo = TODO.objects.all().count()
    return HttpResponseRedirect('/')




class BrandCreateView(APIView):
    def post(self, request):
        print("DEQUEST DATA", request.data)
        brand = request.data.get("brand")
        print("Brand Data", brand)

        serializer = BrandSerializer(data=brand)
        if serializer.is_valid(raise_exception=True):
            brand_saved = serializer.save()
        return Response("Succes: Brand '{}' created succesfully")

class GenderCreateView(APIView):
    def post(self, request):
        print("DEQUEST DATA", request.data)
        gender = request.data.get("gender")
        print("Gender Data", gender)

        serializer = GenderSerializer(data=gender)
        if serializer.is_valid(raise_exception=True):
            gender_saved = serializer.save()
        return Response("Succes: Gender '{}' created succesfully".format(gender_saved))




class RegistrationAPIView(APIView):
    """
    Разрешить всем пользователям (аутентифицированным и нет) доступ к данному эндпоинту.
    """
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Паттерн создания сериализатора, валидации и сохранения - довольно
        # стандартный, и его можно часто увидеть в реальных проектах.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginAPIView(APIView):

    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Обратите внимание, что мы не вызываем метод save() сериализатора, как
        # делали это для регистрации. Дело в том, что в данном случае нам
        # нечего сохранять. Вместо этого, метод validate() делает все нужное.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # Здесь нечего валидировать или сохранять. Мы просто хотим, чтобы
        # сериализатор обрабатывал преобразования объекта User во что-то, что
        # можно привести к json и вернуть клиенту.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Паттерн сериализации, валидирования и сохранения - то, о чем говорили
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
