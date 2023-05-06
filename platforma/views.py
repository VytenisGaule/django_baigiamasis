from abc import ABC
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import generic
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseRedirect

from .models import Origin, HScode, HSTariff, Distributor, Forwarder, Customer, Item, ShoppingCart, \
    ShoppingCartItem, ContractDelivery
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
        if request.user.is_authenticated and hasattr(request.user, 'distributor') and item.distributor == request.user.distributor:
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
