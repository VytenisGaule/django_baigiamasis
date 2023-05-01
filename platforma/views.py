from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import generic
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse

from .models import Origin, HScode, HSTariff, Distributor, Forwarder, Customer
from .forms import UserUpdateForm, DistributorUpdateForm, ForwarderUpdateForm, CustomerUpdateForm


def index(request):
    data = {}
    return render(request, 'index.html', context=data)


class DistributorListView(generic.ListView):
    model = Distributor
    template_name = 'distributor_list.html'
    context_object_name = 'distributor_list'


class DistributorDetailView(generic.DetailView):
    model = Distributor
    template_name = 'distributor_detail_html'


class ForwarderListView(generic.ListView):
    model = Forwarder
    template_name = 'forwarder_list.html'
    context_object_name = 'forwarder_list'


class ForwarderDetailView(generic.DetailView):
    model = Forwarder
    template_name = 'forwarder_detail_html'


class CustomerListView(generic.ListView):
    model = Customer
    template_name = 'customer_list.html'
    context_object_name = 'customer_list'


class CustomerDetailView(generic.DetailView):
    model = Customer
    template_name = 'customer_detail_html'


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
        profile_form = form_class(request.POST, instance=profile)
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
