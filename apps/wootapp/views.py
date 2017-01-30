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
	cart = Carts.objects.filter(user_id=id)
	rating = "1"
	context = {'cart':cart, 'rating':rating}
	return render(request, 'wootapp/cart.html', context)	
def item(request, id):
	try:
		item = Items.objects.get(id=id)
		discussion = Discussion.objects.get(item_id=id).order_by('-created_at')
		items_left = Purchased.objects.filter(item_id=id).filter(user_id=request.session['id']).count()
		items_left = item.units - items_left
		rating = Rating.objects.filter(item_id=id).aggregate(Avg('rating'))
		context = {'item': item, 'discussion': discussion,'items_left': items_left, 'rating':rating}
		return render(request, 'wootapp/item.html', context)
	except:
		return redirect('/')
def add_rating(request):
	rating = request.POST['rating']
	item_id = request.POST['hidden']
	try:
		Rating.objects.get(items_id=item_id, user_id=request.session['id'])
	except:
		pass

def checkout(request):
	return render(request, 'wootapp/checkout.html')
