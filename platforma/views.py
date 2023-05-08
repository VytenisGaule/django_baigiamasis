from abc import ABC
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import generic
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.core.files import File
from django.core.files.base import ContentFile
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.utils import timezone
import openpyxl
from openpyxl.styles import Font
import io

from .models import Origin, HScode, HSTariff, Distributor, Forwarder, Customer, Item, ShoppingCart, \
    ShoppingCartItem, ContractDelivery, Shipment, ShipmentManager
from .forms import *


def index(request):
    data = {}
    return render(request, 'index.html', context=data)


class DistributorListView(generic.ListView):
    model = Distributor
    template_name = 'distributor_list.html'
    context_object_name = 'distributor_list'


class DistributorDetailView(generic.DetailView):
    model = Distributor
    template_name = 'distributor_detail.html'


class ForwarderListView(generic.ListView):
    model = Forwarder
    template_name = 'forwarder_list.html'
    context_object_name = 'forwarder_list'


class ForwarderDetailView(generic.DetailView):
    model = Forwarder
    template_name = 'forwarder_detail.html'


class CustomerListView(generic.ListView):
    model = Customer
    template_name = 'customer_list.html'
    context_object_name = 'customer_list'


class CustomerDetailView(generic.DetailView):
    model = Customer
    template_name = 'customer_detail.html'


class ItemListView(generic.ListView):
    model = Item
    paginate_by = 12
    template_name = 'item_list.html'
    context_object_name = 'item_list'


class ItemDetailView(generic.DetailView):
    model = Item
    template_name = 'item_detail.html'

    """Jei prisijungęs vartotojas yra prekės savininkas - redirektina į distributoriaus vievs"""

    def dispatch(self, request, *args, **kwargs):
        item = self.get_object()
        if request.user.is_authenticated and hasattr(request.user,
                                                     'distributor') and item.distributor == request.user.distributor:
            return redirect('distributor_item_detail', distributor_id=request.user.distributor.pk, pk=item.pk)
        return super().dispatch(request, *args, **kwargs)


class ShoppingCartView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = ShoppingCart
    template_name = 'customer_cart.html'

    def test_func(self):
        user = self.request.user
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        return customer.customer_user == user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_id = self.kwargs.get('customer_id')
        carts = ShoppingCart.objects.filter(customer_id=customer_id).all()
        if all(cart.items_price and cart.delivery_price for cart in carts):
            checkout = sum(cart.items_price + cart.delivery_price + cart.duty for cart in carts)
        else:
            checkout = None
        context['checkout'] = checkout
        return context

    def get_queryset(self):
        customer_id = self.kwargs.get('customer_id')
        return ShoppingCart.objects.filter(customer_id=customer_id)


class AddToCartView(LoginRequiredMixin, generic.View):

    @staticmethod
    def get(request, item_id, distributor_id):
        item = Item.objects.get(pk=item_id)
        user = request.user
        cart = ShoppingCart.objects.filter(customer=user.customer, distributor=item.distributor).first()
        if not cart:
            cart = ShoppingCart.objects.create(customer=user.customer, distributor=item.distributor)
        cart_item = ShoppingCartItem.objects.filter(cart=cart, item=item).first()
        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
        else:
            ShoppingCartItem.objects.create(cart=cart, item=item)
        return redirect('mycart_endpoint', customer_id=user.customer.id)


class ShoppingCartUpdateDeliveryView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    form_class = CartDeliveryForm
    template_name = 'update_delivery.html'

    def test_func(self):
        user = self.request.user
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        return customer.customer_user == user

    def get(self, request, *args, **kwargs):
        shopping_cart = get_object_or_404(ShoppingCart, pk=kwargs['pk'])
        customer_region = shopping_cart.customer.region
        form = self.form_class(distributor_id=shopping_cart.distributor.id)
        delivery_types = []
        for delivery_type in ContractDelivery.DELIVERY_TYPES:
            delivery_type_code = delivery_type[0]
            contract_delivery = ContractDelivery.objects.filter(
                distributor_id_id=shopping_cart.distributor_id,
                region=shopping_cart.customer.region,
                delivery=delivery_type_code
            ).first()
            if contract_delivery:
                delivery_types.append((delivery_type_code, delivery_type[1]))
        form.fields['delivery_type'].choices = delivery_types
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        shopping_cart = get_object_or_404(ShoppingCart, pk=kwargs['pk'])
        form = self.form_class(request.POST, distributor_id=shopping_cart.distributor.id)
        if form.is_valid():
            shopping_cart.cart_delivery_type = form.cleaned_data['delivery_type']
            shopping_cart.save()
            return HttpResponseRedirect(reverse('mycart_endpoint', kwargs={'customer_id': shopping_cart.customer.id}))
        return render(request, self.template_name, {'form': form})


class ShoppingCartDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = ShoppingCart
    template_name = 'customer_cart_delete.html'

    def get(self, request, *args, **kwargs):
        print(kwargs)  # This will print the URL parameters passed to the view
        return super().get(request, *args, **kwargs)

    def test_func(self):
        user = self.request.user
        customer_id = self.kwargs.get('customer_id')
        cart_id = self.kwargs.get('pk')
        customer = get_object_or_404(Customer, id=customer_id)
        shopping_cart = get_object_or_404(ShoppingCart, id=cart_id, customer=customer)
        return customer.customer_user == user and shopping_cart is not None

    def get_success_url(self):
        customer_id = self.kwargs.get('customer_id')
        return reverse_lazy('mycart_endpoint', kwargs={'customer_id': customer_id})


class ShoppingCartItemView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = ShoppingCartItem
    template_name = 'customer_cart_items.html'

    def test_func(self):
        user = self.request.user
        customer_id = self.kwargs.get('customer_id')
        cart_id = self.kwargs.get('cart_id')
        customer = get_object_or_404(Customer, id=customer_id)
        shopping_cart = get_object_or_404(ShoppingCart, id=cart_id, customer=customer)
        return customer.customer_user == user and shopping_cart is not None

    def get_queryset(self):
        cart_id = self.kwargs.get('cart_id')
        return ShoppingCartItem.objects.filter(cart_id=cart_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.kwargs.get('cart_id')
        context['cart_obj'] = get_object_or_404(ShoppingCart, id=cart_id)
        return context


class ShoppingCartItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = ShoppingCartItem
    fields = ['quantity']
    template_name = 'customer_cart_items.html'

    def test_func(self):
        user = self.request.user
        customer_id = self.kwargs.get('customer_id')
        cart_id = self.kwargs.get('cart_id')
        customer = get_object_or_404(Customer, id=customer_id)
        shopping_cart = get_object_or_404(ShoppingCart, id=cart_id, customer=customer)
        return customer.customer_user == user and shopping_cart is not None

    def get_queryset(self):
        cart_id = self.kwargs.get('cart_id')
        return ShoppingCartItem.objects.filter(cart_id=cart_id)

    def post(self, request, *args, **kwargs):
        cart_item = self.get_object()
        quantity = int(request.POST.get('quantity', cart_item.quantity))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cartitem_endpoint', customer_id=self.kwargs['customer_id'], cart_id=self.kwargs['cart_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.kwargs.get('cart_id')
        context['cart_obj'] = get_object_or_404(ShoppingCart, id=cart_id)
        return context

    def get_success_url(self):
        customer_id = self.kwargs['customer_id']
        cart_id = self.kwargs['cart_id']
        return reverse_lazy('cartitem_endpoint', kwargs={'customer_id': customer_id, 'cart_id': cart_id})


class PurchaseAndPayView(LoginRequiredMixin, UserPassesTestMixin, generic.FormView):
    """Ištrinamas krepšelis ir jo pagrindu suformuojami kroviniai"""
    template_name = 'checkout.html'
    form_class = PaymentForm
    success_url = reverse_lazy('items_endpoint')

    def test_func(self):
        user = self.request.user
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        return customer.customer_user == user

    def create_invoice(self, cart):
        """Sukuriamas invoisas kiekvienam kroviniui, saugoma media/invoices"""
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.merge_cells('D1:E1')
        sheet['D1'] = 'INVOICE'
        sheet['D1'].font = Font(bold=True, size=20)
        sheet['D2'] = 'issued'
        sheet['E2'] = cart.created_at.strftime('%Y-%m-%d')
        sheet['A5'] = 'SELLER'
        sheet['A5'] = str(cart.distributor.company_name)
        sheet['A5'].font = Font(bold=True)
        sheet['A6'] = str(cart.distributor.registration_code)
        sheet['A7'] = str(cart.distributor.address)
        sheet['A9'] = 'BUYER'
        sheet['A10'] = str(cart.customer.name)
        sheet['A10'].font = Font(bold=True)
        sheet['A11'] = str(cart.customer.address)
        sheet['A13'] = 'Item'
        sheet['B13'] = 'HS code'
        sheet['C13'] = 'Quantity'
        sheet['E13'] = 'Price'
        sheet['G13'] = 'Total'
        counter = len(cart.shoppingcartitem_set.all()) + 14
        for i, item in enumerate(cart.shoppingcartitem_set.all(), start=14):
            sheet[f'A{i}'] = item.item.name
            sheet[f'B{i}'] = str(item.item.hs_tariff_id.hs_code_id)
            sheet[f'C{i}'] = item.quantity
            sheet[f'D{i}'] = 'pcs.'
            sheet[f'E{i}'] = item.item.price
            sheet[f'F{i}'] = 'EUR'
            sheet[f'G{i}'] = item.subtotal
            sheet[f'H{i}'] = 'EUR'
        sheet[f'A{counter}'] = 'Freight charges'
        sheet[f'G{counter}'] = cart.delivery_price + cart.duty
        sheet[f'A{counter+1}'] = 'Total items'
        sheet[f'G{counter+1}'] = cart.items_price
        sheet[f'A{counter+2}'] = 'Total pay'
        sheet[f'G{counter+2}'] = cart.delivery_price + cart.duty + cart.items_price

        filename = ''.join((str(cart.id), 'invoice.xlsx'))
        with io.BytesIO() as buffer:
            wb.save(buffer)
            buffer.seek(0)
            invoice_data = buffer.read()
        invoice_file = ContentFile(invoice_data, name=filename)
        return invoice_file

    def create_shipments_for_customer(self, customer_id):
        """Sukuriami kroviniai pagal vartotojo krepšelį kiekvienam pardavėjui atskirai"""
        customer = get_object_or_404(Customer, id=customer_id)
        shopping_carts = customer.shoppingcart_set.all()
        for shopping_cart in shopping_carts:
            contract_deliveries = ContractDelivery.objects.filter(
                region=customer.region,
                delivery=shopping_cart.cart_delivery_type,
                distributor_id__in=shopping_carts.values_list('distributor', flat=True)
            )
            contract_delivery = contract_deliveries.first()
            shipment = Shipment.objects.create(
                total_price=shopping_cart.items_price + shopping_cart.delivery_price + shopping_cart.duty,
                duty=shopping_cart.duty,
                invoice=self.create_invoice(shopping_cart),
                distributor=shopping_cart.distributor,
                customer=shopping_cart.customer,
                forwarder=contract_delivery.forwarder_id,
            )
            shopping_cart.delete()

    def form_valid(self, form):
        customer_id = self.kwargs['customer_id']
        self.create_shipments_for_customer(customer_id)
        return super().form_valid(form)


class ItemByDistributorListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Item
    paginate_by = 12
    template_name = 'distributor_item_list.html'

    def test_func(self):
        user = self.request.user
        distributor_id = self.kwargs.get('distributor_id')
        distributor = get_object_or_404(Distributor, id=distributor_id)
        return distributor.distributor_user == user

    def get_queryset(self):
        distributor = self.request.user.distributor
        return Item.objects.filter(distributor=distributor)


class ItemByDistributorCreate(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Item
    template_name = 'distributor_new_item.html'
    form_class = DistributorItemCreateForm

    def test_func(self):
        user = self.request.user
        distributor_id = self.kwargs.get('distributor_id')
        distributor = get_object_or_404(Distributor, id=distributor_id)
        return distributor.distributor_user == user

    def get_form_kwargs(self):
        """Perduodamas prisijungusio user objektas į forms.py"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        distributor_id = self.kwargs.get('distributor_id')
        return reverse_lazy('distributor_items_endpoint', kwargs={'distributor_id': distributor_id})


class ItemByDistributorUpdate(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Item
    template_name = 'distributor_edit_item.html'
    form_class = DistributorItemCreateForm

    def test_func(self):
        user = self.request.user
        distributor_id = self.kwargs.get('distributor_id')
        distributor = get_object_or_404(Distributor, id=distributor_id)
        return distributor.distributor_user == user

    def get_form_kwargs(self):
        """Perduodamas prisijungusio user objektas į forms.py"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        distributor_id = self.kwargs.get('distributor_id')
        return reverse_lazy('distributor_items_endpoint', kwargs={'distributor_id': distributor_id})


class ItemByDistributorDelete(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Item
    template_name = 'distributor_delete_item.html'

    def test_func(self):
        user = self.request.user
        distributor_id = self.kwargs.get('distributor_id')
        distributor = get_object_or_404(Distributor, id=distributor_id)
        return distributor.distributor_user == user

    def get_success_url(self):
        distributor_id = self.kwargs.get('distributor_id')
        return reverse_lazy('distributor_items_endpoint', kwargs={'distributor_id': distributor_id})


class ItemByDistributorView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = Item
    template_name = 'distributor_item_detail.html'

    def test_func(self):
        user = self.request.user
        distributor_id = self.kwargs.get('distributor_id')
        distributor = get_object_or_404(Distributor, id=distributor_id)
        return distributor.distributor_user == user


class ShipmentsByForwarderListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Shipment
    paginate_by = 20
    template_name = 'forwarder_shipment_list.html'

    def test_func(self):
        user = self.request.user
        forwarder_id = self.kwargs.get('forwarder_id')
        forwarder = get_object_or_404(Forwarder, id=forwarder_id)
        return forwarder.forwarder_user == user

    def get_queryset(self):
        forwarder = self.request.user.forwarder
        return Shipment.objects.filter(forwarder=forwarder)


class ShipmentLocationsView(LoginRequiredMixin, generic.ListView):
    template_name = 'shipment_locations.html'
    context_object_name = 'locations'

    def get_queryset(self):
        return Shipment.LOCATION_CHOICES


class ShipmentsAtLocationView(LoginRequiredMixin, generic.ListView):
    model = Shipment
    paginate_by = 20
    template_name = 'shipments_at_location.html'
    context_object_name = 'shipment_list'

    def get_queryset(self):
        user = self.request.user
        location = self.kwargs.get('location')
        query = Q(location=location) & (
            Q(distributor__distributor_user=user) |
            Q(customer__customer_user=user) |
            Q(forwarder__forwarder_user=user)
        )
        return Shipment.objects.filter(query)


class ShipmentsAtLocationForwarderView(LoginRequiredMixin, generic.ListView):
    model = Shipment
    paginate_by = 20
    template_name = 'update_shipment_location.html'
    context_object_name = 'shipment_list'

    def get_queryset(self):
        user = self.request.user
        query = Q(forwarder__forwarder_user=user)
        return Shipment.objects.filter(query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Shipment.LOCATION_CHOICES
        return context

    def post(self, request, forwarder_id):
        selected_shipments = request.POST.getlist('selected_shipments[]')
        new_location = request.POST.get('new_location')
        for shipment_id in selected_shipments:
            shipment = Shipment.objects.get(pk=shipment_id)
            shipment.location = new_location
            shipment.save()
        return redirect('shipment_update_endpoint', forwarder_id=forwarder_id)


class ShipmentDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = Shipment
    template_name = 'shipment_detail.html'

    def test_func(self):
        user = self.request.user
        distributor_id = self.kwargs.get('distributor_id')
        distributor = get_object_or_404(Distributor, id=distributor_id)
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        forwarder_id = self.kwargs.get('forwarder_id')
        forwarder = get_object_or_404(Forwarder, id=forwarder_id)
        return distributor.distributor_user == user \
            or customer.customer_user == user \
            or forwarder.forwarder_user == user

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object, now=timezone.now())
        return self.render_to_response(context)


"""reikės stipresnių passwordų"""


@csrf_protect
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username %s already exists!!!" % username)
            return redirect('register_endpoint')
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email %s already exists!!!" % email)
            return redirect('register_endpoint')
        elif password != password2:
            messages.error(request, "Passwords doesn't match!!!")
            return redirect('register_endpoint')
        else:
            User.objects.create_user(username=username, password=password, email=email)
            messages.info(request, "User %s registered successfuly" % username)
            return redirect('login')
    else:
        return render(request, 'registration/register.html')


@login_required
def profilis(request):
    user = request.user
    if user.groups.filter(name='distributor').exists():
        profile = user.distributor
        form_class = DistributorUpdateForm
    elif user.groups.filter(name='forwarder').exists():
        profile = user.forwarder
        form_class = ForwarderUpdateForm
    elif user.groups.filter(name='customer').exists():
        profile = user.customer
        form_class = CustomerUpdateForm
    else:
        raise Http404

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=user)
        profile_form = form_class(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and profile_form.is_valid():
            u_form.save()
            profile_form.save()
            messages.success(request, f"Profilis atnaujintas")
            return redirect('profile_endpoint')
    else:
        u_form = UserUpdateForm(instance=user)
        profile_form = form_class(instance=profile)

    data = {
        'u_form_cntx': u_form,
        'profile_form_cntx': profile_form,
    }

    return render(request, "profilis.html", context=data)


def search(request):
    query_text = request.GET.get('search_text')
    if query_text:
        query_result = Item.objects.filter(
            Q(name__icontains=query_text) |
            Q(description__icontains=query_text) |
            Q(distributor__company_name__icontains=query_text) |
            Q(distributor__about__icontains=query_text) |
            Q(distributor__distributor_user__username__icontains=query_text)
        )
        paginator = Paginator(query_result, 12)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
    else:
        query_result = []
        page_obj = None
    data = {'query_result_cntx': query_result, 'page_obj': page_obj, 'query_text': query_text}
    return render(request, 'search.html', context=data)
