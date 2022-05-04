from django.core.signals import request_started
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, post_init, pre_save
from django.conf import settings

from shop.models import Product


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def post_save_user(created, **kwargs):
    instance = kwargs['instance']
    if created:
        print(f'Пользователь {instance.username} создан (post_save)')
    else:
        print(f'Пользователь {instance.username} обновлен (post_save)')

@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def post_remove_user(**kwargs):
    instance = kwargs['instance']
    print(f'Пользователь {instance.username} удален (post_delete)')

#
# @receiver(post_init, sender=Product)
# def post_init_product(**kwargs):
#     instance = kwargs['instance']
#     print(f'Продукт {instance.name} инициализирован (post_init)')

# @receiver(pre_save, sender=settings.AUTH_USER_MODEL)
# def pre_save_user(created, **kwargs):
#     instance = kwargs['instance']
#     if created:
#         print(f'Пользователь {instance.username} создан (pre_save)')
#     else:
#         print(f'Пользователь {instance.username} обновлен(pre_save)')



