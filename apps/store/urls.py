from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path(
        'tienda/checkout/',
        views.checkout,
        name='checkout',
    ),
    path(
        'tienda/checkout/resultado/',
        views.checkout_result,
        name='checkout_result',
    ),
]
