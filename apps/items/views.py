from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Avg
from django.contrib import messages
from django.shortcuts import get_object_or_404
import datetime
from forms import CreditCardForm
from .models import *
from ..users.models import Users
from .models import Items, Purchases, Discussions

def index(request):
    return render(request, 'items/index.html')

def browse(request):
    return render(request, 'items/browse.html')

def create_deal(request):
    return render(request, 'items/create_deal.html')

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
                return redirect('items:cart')
        return render(request, 'items/cart.html', {'cart_items': cart_items, 'rating': rating, 'form': form})
    return redirect('users:login')

def item(request, id):
    item = get_object_or_404(Items, id=id)
    discussion = Discussions.objects.filter(item_id=id)
    items_left = Purchases.objects.filter(item_id=id).filter(user_id=request.session['id']).count()
    items_left = item.units - items_left
    imageurl = str(item.image)
    item.image = imageurl.replace("apps/items","",1)
    rating_count = Ratings.objects.filter(item_id=item).count()
    print rating_count
    try:
        r = Ratings.objects.get(user_id=request.session['id'],item_id=id)
    except:
        r = 0
    context = {'item': item, 'discussion': discussion,'items_left': items_left, 'r': r}
    return render(request, 'items/item.html', context)

def add_rating(request):
    rate = request.POST['rating']
    item = request.POST['hidden']
    user = request.session['id']
    try:
        r = Ratings.objects.get(user_id=user, item_id=item)
        Ratings.objects.filter(user_id=user).filter(item_id=item).update(rating=rate)
        return redirect('items:item', id=item)
    except:
        Ratings.objects.create(item_id=item, user_id=user, rating=rate)
        return redirect('items:item', id=item)
def add_item(request):
    if request.method == 'POST':
        Items.objects.add(request.POST['name'], request.POST['description'], request.POST['price'], request.POST['units'], request.POST['category'], request.FILES['image'])
    return redirect(reverse('items:create_deal'))

    #NEEDED TO ACCESS IMAGES FROM THIERE SAVED LOCATION
    # item = Items.objects.get(id=2)
    # imageurl = str(item.image)
    # item.image = imageurl.replace("apps/items","",1)
    # context = {'item':item, 'imageurl':imageurl}
