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

from django.http import HttpResponse

from .models import Origin, HScode, HSTariff, Distributor, Forwarder, Customer, Item, ShoppingCart, \
    ShoppingCartItem
from .forms import UserUpdateForm, DistributorUpdateForm, ForwarderUpdateForm, CustomerUpdateForm, \
    ShoppingCartItemForm


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


class ShoppingCartView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = ShoppingCart
    template_name = 'customer_cart.html'

    def test_func(self):
        user = self.request.user
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        return customer.customer_user == user

    def get_queryset(self):
        customer_id = self.kwargs.get('customer_id')
        return ShoppingCart.objects.filter(customer_id=customer_id)


class ShoppingCartUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = ShoppingCart
    fields = ['cart_delivery_type']
    template_name = 'customer_cart.html'

    def test_func(self):
        user = self.request.user
        customer_id = self.kwargs.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        return customer.customer_user == user

    def get_queryset(self):
        customer_id = self.kwargs.get('customer_id')
        return ShoppingCart.objects.filter(customer_id=customer_id)

    def post(self, request, customer_id, pk):
        cart_obj = get_object_or_404(ShoppingCart, pk=pk)
        form = ShoppingCartForm(request.POST, instance=cart_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Delivery type updated successfully')
        else:
            messages.error(request, f'Error updating delivery type')
        return redirect('mycart_endpoint', customer_id=customer_id)


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


# class ShoppingCartItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView, ABC):
#     model = ShoppingCartItem
#     template_name = 'customer_cart_items.html'
#     success_url = 'mycart/<int:customer_id>/<int:cart_id>/'
#
#     def test_func(self):
#         user = self.request.user
#         customer_id = self.kwargs.get('customer_id')
#         cart_id = self.kwargs.get('cart_id')
#         customer = get_object_or_404(Customer, id=customer_id)
#         shopping_cart = get_object_or_404(ShoppingCart, id=cart_id, customer=customer)
#         return customer.customer_user == user and shopping_cart is not None
#
#     def get_queryset(self):
#         cart_id = self.kwargs.get('cart_id')
#         return ShoppingCartItem.objects.filter(cart_id=cart_id)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         cart_id = self.kwargs.get('cart_id')
#         context['cart_obj'] = get_object_or_404(ShoppingCart, id=cart_id)
#         return context

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
