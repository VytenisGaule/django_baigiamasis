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

from .models import Origin, HScode, HSTariff, Distributor
from .forms import UserUpdateForm, DistributorUpdateForm


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
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        d_form = DistributorUpdateForm(request.POST, instance=request.user.distributor_user)
        if u_form.is_valid() and d_form.is_valid():
            u_form.save()
            d_form.save()
            messages.success(request, f"Profilis atnaujintas")
            return redirect('profilis_endpoint')
    else:
        u_form = UserUpdateForm(instance=request.user)
        d_form = DistributorUpdateForm(instance=request.user.distributor_user)

    data = {
        'u_form_cntx': u_form,
        'd_form_cntx': d_form,
    }

    return render(request, "profilis.html", context=data)
