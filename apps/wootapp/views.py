from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Avg
from django.contrib import messages
import datetime
from forms import CreditCardForm
from .models import *
from ..loginapp.models import Users
from .models import Items, Purchases

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
	user = Users.objects.get(id=request.session['id'])
	purchases = Purchases.objects.filter(user=user)
	rating = "1"
	context = {'purchases':purchases, 'rating':rating}
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
        Items.objects.add(request.POST['name'], request.POST['description'], request.POST['price'], request.POST['units'], request.POST['category'], request.FILES['image'])
    return redirect(reverse('woot:create_deal'))

def checkout(request):
    customer = Users.objects.get(id=request.session['id'])
    cart_items = Items.objects.filter(item_purchased__status='open')
    purchased_items = Items.objects.filter(item_purchased__status='closed')
    form = CreditCardForm()

    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            for item in customer.purchases_set.filter(status='open'):
                item.charge(item.product.price*100, request.POST['number'], request.POST['expiration_0'], request.POST['expiration_1'], request.POST['cvc'])
            messages.success(request, 'Products purchased!')
            return redirect('woot:checkout')
    return render(request, 'wootapp/checkout.html', {'cart_items': cart_items, 'purchased_items':purchased_items, 'form': form})


    #NEEDED TO ACCESS IMAGES FROM THIERE SAVED LOCATION
    # item = Items.objects.get(id=2)
    # imageurl = str(item.image)
    # item.image = imageurl.replace("apps/wootapp","",1)
    # context = {'item':item, 'imageurl':imageurl}
