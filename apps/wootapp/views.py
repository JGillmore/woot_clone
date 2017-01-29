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
	id = request.session['id']
	cart = Carts.objects.get(user_id=id)
	rating = "1"
	context = {'cart':cart, 'rating':rating}
	return render(request, 'wootapp/cart.html', context)
def item(request, id):
	try:
		item = Items.objects.get(id=id)
		discussion = Discussion.objects.get(item_id=id).order_by('-created_at')
		context = {'item': item, 'discussion': discussion}
		return render(request, 'wootapp/item.html', context)
	except:
		return redirect('/')

def checkout(request):
    return render(request, 'wootapp/checkout.html')
