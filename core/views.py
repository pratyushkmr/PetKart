from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order,Address,Payment,UserProfile,Coupon,Refund
from django.utils import timezone
from django.views.generic import ListView, DetailView,View
from .forms import Checkoutform, CouponForm, RefundForm, PaymentForm
import stripe,string
from django.conf import settings
import random
stripe.api_key=settings.STRIPE_TEST_KEY

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase+string.digits,k=20))

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid    


class HomeView(ListView):
    model=Item
    paginate_by= 2
    template_name="homepg.html"

class CheckoutView(View):
     def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = Checkoutform()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")       
        
     def post(self, *args, **kwargs):
         form = Checkoutform(self.request.POST or None)
         try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
    
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
    
                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()
    
                        order.shipping_address = shipping_address
                        order.save()
    
                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
    
                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")
    
                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')
    
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
    
                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')
    
                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()
    
                        order.billing_address = billing_address
                        order.save()
    
                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
    
                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")
    
                payment_option = form.cleaned_data.get('payment_option')
    
                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
         except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")
        
class PaymentView(View):
    def get(self, *args, **kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
        except Order.DoesNotExist:
            order = None
        #if order.billing_address:
        context={
                'order':order,
                'DISPLAY_COUPON_FORM': False
                }
        return render(self.request, 'payment.html',context)
        #else:
            #return redirect("core:payment")
    
    def post(self,wargs, **kwargs):
        order=Order.objects.get(user=self.request.user,ordered=False)
        amount=int(order.get_total()*75)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')
            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)
        
                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

        try:
            if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
            else:
                charge=stripe.Charge.create(
                amount=amount,
                currency="Rs.",
                source=token)
  # Use Stripe's library to make requests...
            payment=Payment()
            payment.stripe_charge_id=charge['id']
            payment.user=self.request.user
            payment.amount=order.get_total()
            payment.save()
            
            order_items=order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
            
            order.ordered=True
            order.payment=payment
            order.ref_code=create_ref_code()
            order.save()
            messages.success(self.request,"Order is successful")  
            return redirect("/")
    
        except stripe.error.CardError as e:
              body=e.jsom_body
              err=body.get('error',{})
              messages.error(self.request, f"{err.get('message')}")
              return redirect("/")
              
        except stripe.error.RateLimitError as e:
          # Too many requests made to the API too quickly
          messages.error(self.request,"Rate limit error")
          return redirect("/")
        except stripe.error.InvalidRequestError as e:
          # Invalid parameters were supplied to Stripe's API
          messages.error(self.request, "Invalid Parameter")
          return redirect("/")
        except stripe.error.AuthenticationError as e:
          # Authentication with Stripe's API failed
          # (maybe you changed API keys recently)
          messages.error(self.request, "Not authenticated")
          return redirect("/")
        except stripe.error.APIConnectionError as e:
          # Network communication with Stripe failed
          messages.error(self.request, "Network error")
          return redirect("/")
        except stripe.error.StripeError as e:
          # Display a very generic error to the user, and maybe send
          # yourself an email
          messages.error(self.request, "Something went wrong, you were not charged")
          return redirect("/")
        except Exception as e:
          # Something else happened, completely unrelated to Stripe
          messages.error(self.request, "A serious error occured")
          return redirect("/")
            
    
class OrderSummaryView(LoginRequiredMixin,View):
    def get(self, wargs, **kwargs):
        try:
            order=Order.objects.get(user=self.request.user, ordered=False)
            context={
                    'object':order}
            return render(self.request, 'order_summary.html',context)

        except ObjectDoesNotExist:
            messages.error(self.request, "No active order")
            return redirect("/")

class ItemDetailView(DetailView):
    model=Item
    template_name="productpg.html"
    
@login_required
def add_to_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_item, created=OrderItem.objects.get_or_create(
            item=item, 
            user=request.user,
            ordered=False)
    order_qs=Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity+=1
            order_item.save()
            messages.info(request,"was updated")
            return redirect("core:OrderSummaryView")
        else:
            messages.info(request,"was added")
            order.items.add(order_item)
            return redirect("core:OrderSummaryView")
    else:
        ordered_date=timezone.now()
        order=Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        return redirect("core:OrderSummaryView")

@login_required
def remove_from_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_qs=Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request,"was removed")
            return redirect("core:OrderSummaryView")
        else:
            messages.info(request,"was not there")

            return redirect("core:product", slug=slug)
    else:
        messages.info(request,"no order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_qs=Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False)[0]
            if order_item.quantity>1:
                order_item.quantity-=1
            else:
                order.items.remove(order_item)
            order_item.save()
            messages.info(request,"quantity was updated")
            return redirect("core:OrderSummaryView")

        else:
            messages.info(request,"was not there")

            return redirect("core:product", slug=slug)
    else:
        messages.info(request,"no order")
        return redirect("core:product", slug=slug)
    return redirect("core:product", slug=slug)

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")



