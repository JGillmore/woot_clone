from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Avg
from django.contrib import messages
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
	item = Items.objects.get(id=id)
	discussion = Discussions.objects.filter(item_id=id)
	items_left = Purchased.objects.filter(item_id=id).filter(user_id=request.session['id']).count()
	items_left = item.units - items_left
	imageurl = str(item.image)
	print imageurl
	item.image = imageurl.replace("apps/wootapp","",1)
	print item.image
	context = {'item': item, 'discussion': discussion,'items_left': items_left}
	return render(request, 'wootapp/item.html', context)


def add_rating(request):
	rating = request.POST['rating']
	item = request.POST['hidden']
	user = request.session['id']
	try:
		Ratings.objects.all()
		print '1'
		messages.add_message(request, messages.ERROR, 'You have already rated this item')
		return redirect('/item/'+item)
	except:
		print '2'
		Ratings.objects.create(item_id=item, user_id=user, rating=rating)
	return redirect('/item/'+item)

def add_item(request):
    if request.method == 'POST':
        print request.POST
        print request.FILES
        Items.objects.add(request.POST['name'], request.POST['description'], request.POST['price'], request.POST['units'], request.POST['category'], request.FILES['image'])
    return redirect(reverse('woot:create_deal'))

def checkout(request):
    return render(request, 'wootapp/checkout.html')


    #NEEDED TO ACCESS IMAGES FROM THIERE SAVED LOCATION
    # item = Items.objects.get(id=2)
    # imageurl = str(item.image)
    # item.image = imageurl.replace("apps/wootapp/","",1)
    # context = {'item':item, 'imageurl':imageurl}
