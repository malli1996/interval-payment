from django.views.generic.base import RedirectView
import stripe
from django.conf import UserSettingsHolder, settings
from django.http import JsonResponse
from django.views import View
from .models import Price, Product, StripeCustomer
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.shortcuts import render,redirect

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.mail import send_mail

stripe.api_key = settings.STRIPE_PRIVATE_KEY


class SuccessView(TemplateView):
    template_name = "success.html"

class CancelView(TemplateView):
    template_name = "cancel.html"


class ProductLandingPageView(TemplateView):
    template_name = "paymentpage.html"

    def get_context_data(self, **kwargs):
        product = Product.objects.get(name="yoga")
        print(product)
        prices = Price.objects.filter(product=product)
        print(prices)
        context = super(ProductLandingPageView,
                        self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "prices": prices
        })
        return context

        
class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        price = Price.objects.get(id=self.kwargs["pk"])
        print(price)
        YOUR_DOMAIN = "http://127.0.0.1:8000"  # change in production
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return redirect(checkout_session.url)


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fetch all the required data from session
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')

        # Get the user and create a new StripeCustomer
        StripeCustomer.objects.create(
            stripeCustomerId=stripe_customer_id,
            stripeSubscriptionId=stripe_subscription_id,
        )
        print( ' just subscribed.')

    return HttpResponse(status=200)



def home(request):
    try:
        # Retrieve the subscription & product
        stripe_customer = StripeCustomer.objects.get(user=request.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = stripe.Subscription.retrieve(stripe_customer.stripeSubscriptionId)
        product = stripe.Product.retrieve(subscription.plan.product)

        # Feel free to fetch any additional data from 'subscription' or 'product'
        # https://stripe.com/docs/api/subscriptions/object
        # https://stripe.com/docs/api/products/object

        return render(request, 'home.html', {
            'subscription': subscription,
            'product': product,
        })

    except StripeCustomer.DoesNotExist:
        return render(request, 'home.html')

# from django.conf import settings
# from django.http.response import JsonResponse 
# from django.views.decorators.csrf import csrf_exempt
# from django.views.generic.base import TemplateView
# import stripe
# from django.http.response import JsonResponse, HttpResponse

# class HomePageView(TemplateView):
#     template_name = 'home.html'

# class SuccessView(TemplateView):
#     template_name = 'success.html'


# class CancelledView(TemplateView):
#     template_name = 'cancelled.html'

# @csrf_exempt
# def stripe_config(request):
#     if request.method == 'GET':
#         stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
#         return JsonResponse(stripe_config, safe=False)



# @csrf_exempt
# def create_checkout_session(request):
#     if request.method == 'GET':
#         domain_url = 'http://localhost:8000/'
#         stripe.api_key = settings.STRIPE_PRIVATE_KEY
#         try:
#             # Create new Checkout Session for the order
#             # Other optional params include:
#             # [billing_address_collection] - to display billing address details on the page
#             # [customer] - if you have an existing Stripe Customer ID
#             # [payment_intent_data] - capture the payment later
#             # [customer_email] - prefill the email input in the form
#             # For full details see https://stripe.com/docs/api/checkout/sessions/create

#             # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
#             checkout_session = stripe.checkout.Session.create(
#                 success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
#                 cancel_url=domain_url + 'cancelled/',
#                 payment_method_types=['card'],
#                 mode='payment',
#                 line_items=[
#                     {
#                         'name': 'flask_book',
#                         'quantity': 1,
#                         'currency': 'INR',
#                         'amount': '200000',
#                     }
#                 ]
#             )
#             return JsonResponse({'sessionId': checkout_session['id']})
#         except Exception as e:
#             return JsonResponse({'error': str(e)})


# # @csrf_exempt
# # def stripe_webhook(request):
# #     stripe.api_key = settings.STRIPE_PRIVATE_KEY
# #     endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
# #     payload = request.body
# #     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
# #     event = None

# #     try:
# #         event = stripe.Webhook.construct_event(
# #             payload, sig_header, endpoint_secret
# #         )
# #     except ValueError as e:
# #         # Invalid payload
# #         return HttpResponse(status=400)
# #     except stripe.error.SignatureVerificationError as e:
# #         # Invalid signature
# #         return HttpResponse(status=400)

# #     # Handle the checkout.session.completed event
# #     if event['type'] == 'checkout.session.completed':
# #         print("Payment was successful.")
#             # session = event['data']['object']
#             # customer_email = session["customer_details"]["email"]
#             # payment_intent = session["payment_intent"]

#             # TODO - send an email to the customer

# #     return HttpResponse(status=200)