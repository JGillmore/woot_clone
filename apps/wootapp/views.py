from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
import datetime

from .models import *
from ..loginapp.models import Users

def index(request):
    return render(request, 'wootapp/index.html')

def user(request):
    user = Users.objects.get(id=request.session['id'])
    birth_date = str(user.birth_date)
    context = {'user':user, 'birth_date':birth_date}
    return render(request, 'wootapp/user.html', context)

def browse(request):
    return render(request, 'wootapp/browse.html')

def create_deal(request):
    return render(request, 'wootapp/create_deal.html')

def cart(request):
    return render(request, 'wootapp/cart.html')

def item(request):
    return render(request, 'wootapp/item.html')

def checkout(request):
    return render(request, 'wootapp/checkout.html')
