# -*- coding: utf-8 -*-https://github.com/justdjango/django-ecommerce/blob/master/templates/request_refund.html
from django.urls import path
from .views import (
        ItemDetailView,
        HomeView,
        OrderSummaryView,
        CheckoutView,
        add_to_cart,
        remove_from_cart,
        remove_single_item_from_cart,
        PaymentView,
        AddCouponView,
        RequestRefundView
        )

app_name='core'
urlpatterns = [
    path('',HomeView.as_view(),name='home'),
    path('checkout/',CheckoutView.as_view(),name='checkout'),
    path('order_summary/',OrderSummaryView.as_view(),name='OrderSummaryView'),
    path('product/<slug>/',ItemDetailView.as_view(),name='product'),
    path('add-to-cart/<slug>/',add_to_cart,name='add-to-cart'),
    path('add-coupon/',AddCouponView.as_view(),name='add-coupon'),

    path('remove-from-cart/<slug>/',remove_from_cart,name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/',remove_single_item_from_cart,name='remove-single-item-from-cart'),
    path('payment/', PaymentView.as_view(), name='payment'),
     path('request-refund/', RequestRefundView.as_view(), name='request-refund')
]
