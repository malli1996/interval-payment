from django.contrib import admin
from django.urls import path
from recurring.views import (
    CreateCheckoutSessionView,
    SuccessView,
    CancelView,
    ProductLandingPageView,
    #stripe_webhook,
)

urlpatterns = [
    path('', ProductLandingPageView.as_view(), name='paymentpage'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('create-checkout-session/<pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    #path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    
]


# from django.urls import path

# from . import views

# urlpatterns = [
#     path('', views.HomePageView.as_view(), name='home'),
#     path('config/', views.stripe_config),
#     path('create-checkout-session/', views.create_checkout_session),
#     path('success/', views.SuccessView.as_view()), 
#     path('cancelled/', views.CancelledView.as_view()),
#     #path('webhook/', views.stripe_webhook),

# ]