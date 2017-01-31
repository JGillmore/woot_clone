from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Avg
from django.contrib import messages
from django.shortcuts import get_object_or_404
import datetime
from forms import CreditCardForm
from .models import *
from ..users.models import Users
from .models import Items, Purchases

def browse(request):
    return render(request, 'wootapp/browse.html')

def create_deal(request):
    return render(request, 'wootapp/create_deal.html')

def cart(request):
    if 'id' in request.session:
        user = Users.objects.get(id=request.session['id'])
        cart_items = Items.objects.filter(item_purchased__status='open').filter(item_purchased__user=user)
        rating = "1"
        form = CreditCardForm()

        if request.method == 'POST':
            form = CreditCardForm(request.POST)
            if form.is_valid():
                for item in cart_items:
                    item.charge(item.price*100, request.POST['number'], request.POST['expiration_0'], request.POST['expiration_1'], request.POST['cvc'])
                messages.success(request, 'Products purchased!')
                return redirect('woot:checkout')
        return render(request, 'wootapp/cart.html', {'cart_items': cart_items, 'rating': rating, 'form': form})
    return redirect('users:login')

def item(request, id):
	item = get_object_or_404(Items, id=id)
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

    #NEEDED TO ACCESS IMAGES FROM THIERE SAVED LOCATION
    # item = Items.objects.get(id=2)
    # imageurl = str(item.image)
    # item.image = imageurl.replace("apps/wootapp","",1)
    # context = {'item':item, 'imageurl':imageurl}
