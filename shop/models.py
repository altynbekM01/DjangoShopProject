import time

import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
	AbstractBaseUser, BaseUserManager, PermissionsMixin
)
import os

from django.core.exceptions import ValidationError
from django.db import models

from django.urls import reverse


# Create your models here.



class Category(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'вид обуви'
        verbose_name_plural = 'виды обуви'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


def get_upload_path(instance, filename):
    #  задаем название файла названием slug`а продукта
    filename = instance.slug + '.' + filename.split('.')[1]
    return os.path.join('images/', filename)



class Production(models.Model):
    production = models.TextField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.production

# class Text(BaseContent):
#     body = models.TextField()


class Brand(Production):
    name = models.CharField(max_length=100, db_index=True)
    image = models.ImageField(upload_to='brands', blank=True)
    slug = models.SlugField(max_length=200, db_index=True)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:brands_views',
                       args=[self.slug])

class Gender(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)

    class Meta:
        verbose_name = 'мужское/женское'
        verbose_name_plural = 'мужское/женское'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:gender_views',
                       args=[self.slug])

class PriceManager(models.Manager):
    def show_by_price_function(self, needed_price):
        return super(PriceManager,
		     self).get_queryset()\
                          .filter(price=needed_price)

class StockManager(models.Manager):
    def get_queryset(self):
        return super(StockManager,
		     self).get_queryset()\
                          .filter(stock__gte=5)

class MaleManager(models.Manager):
    def get_queryset(self):
        return super(MaleManager,
		     self).get_queryset()\
                          .filter(gender__name='Male')

class FemaleManager(models.Manager):
    def get_queryset(self):
        return super(FemaleManager,
		     self).get_queryset()\
                          .filter(gender__name='Female')

def validate_price(price):
    if price <= 0:
        raise ValidationError("Цена должна быть больше 0")

def validate_description(description):
    if len(description) < 3:
        raise ValidationError("Описание продукта должно быть не короче 3 символов")

class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name='products',
        on_delete=models.CASCADE
    )
    brand = models.ForeignKey(Brand, related_name='brand', blank=True, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, related_name='gender', blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)
    description = models.TextField(validators=[validate_description])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_price])
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=get_upload_path, blank=True)

    objects = models.Manager()
    show_by_price = PriceManager()
    stock_more_then_5 = StockManager()
    show_male_clothes = MaleManager()
    show_female_clothes = FemaleManager()

    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])


class UserManager(BaseUserManager):
    """
    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager. Унаследовавшись от BaseUserManager, мы получаем много того
    же самого кода, который Django использовал для создания User (для демонстрации).
    """

    def create_user(self, username, email, password=None):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """ Создает и возввращет пользователя с привилегиями суперадмина. """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

class User(AbstractBaseUser, PermissionsMixin):
    # Каждому пользователю нужен понятный человеку уникальный идентификатор,
    # который мы можем использовать для предоставления User в пользовательском
    # интерфейсе. Мы так же проиндексируем этот столбец в базе данных для
    # повышения скорости поиска в дальнейшем.
    username = models.CharField(db_index=True, max_length=255, unique=True)

    # Так же мы нуждаемся в поле, с помощью которого будем иметь возможность
    # связаться с пользователем и идентифицировать его при входе в систему.
    # Поскольку адрес почты нам нужен в любом случае, мы также будем
    # использовать его для входы в систему, так как это наиболее
    # распространенная форма учетных данных на данный момент (ну еще телефон).
    email = models.EmailField(db_index=True, unique=True)

    # Когда пользователь более не желает пользоваться нашей системой, он может
    # захотеть удалить свой аккаунт. Для нас это проблема, так как собираемые
    # нами данные очень ценны, и мы не хотим их удалять :) Мы просто предложим
    # пользователям способ деактивировать учетку вместо ее полного удаления.
    # Таким образом, они не будут отображаться на сайте, но мы все еще сможем
    # далее анализировать информацию.
    is_active = models.BooleanField(default=True)

    # Этот флаг определяет, кто может войти в административную часть нашего
    # сайта. Для большинства пользователей это флаг будет ложным.
    is_staff = models.BooleanField(default=False)

    # Временная метка создания объекта.
    created_at = models.DateTimeField(auto_now_add=True)

    # Временная метка показывающая время последнего обновления объекта.
    updated_at = models.DateTimeField(auto_now=True)

    # Дополнительный поля, необходимые Django
    # при указании кастомной модели пользователя.

    # Свойство USERNAME_FIELD сообщает нам, какое поле мы будем использовать
    # для входа в систему. В данном случае мы хотим использовать почту.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Сообщает Django, что определенный выше класс UserManager
    # должен управлять объектами этого типа.
    objects = UserManager()

    def __str__(self):
        """ Строковое представление модели (отображается в консоли) """
        return self.email

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token(). Декоратор @property выше делает это
        возможным. token называется "динамическим свойством".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        Этот метод требуется Django для таких вещей, как обработка электронной
        почты. Обычно это имя фамилия пользователя, но поскольку мы не
        используем их, будем возвращать username.
        """
        return self.username

    def get_short_name(self):
        """ Аналогично методу get_full_name(). """
        return self.username

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        # dt = datetime.now() + timedelta(days=60)
        #
        # token = jwt.encode({
        #     'id': self.pk,
        #     # 'exp': int(dt.strftime('%S'))
        #     'exp': str(time.mktime(dt.timetuple()))[:-2]
        # }, settings.SECRET_KEY, algorithm='HS256')
        #
        # return token.decode('utf-8')
        dt = datetime.now() + timedelta(days=60)
        token = jwt.encode({
            'id': self.pk,
            'exp': dt.utcfromtimestamp(dt.timestamp())},
            settings.SECRET_KEY, algorithm='HS256')
        return token