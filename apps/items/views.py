from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.db.models import Avg, Sum
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.core.mail import EmailMessage, send_mail
from django.template import Context
import datetime
from forms import CreditCardForm
from .models import *
from ..users.models import Users
from django.db.models import Sum
from .models import Items, Purchases, Discussions

def send_email(user, cart):
    template = get_template('contact_template.txt')
    content = template.render({'first_name': user.first_name, 'purchases': cart})
    # That email you see below, is suppoed to be the customer's email
    email = EmailMessage("Your order",	content, "Woot", [user.email], headers = {'Reply-To': 'wootclone.dojo@gmail.com'})
    email.send()

def index(request):
    deal = DealofTheMinute.objects.get(id=1)
    time_diff = datetime.datetime.now().replace(tzinfo=None) - deal.updated_at.replace(tzinfo=None)
    if int(time_diff.total_seconds()) > -21570: #this is actually checking to see if the time is over 30 seconds old, a new update is -21600 seconds
        if deal.item_id == 18:
            deal.item_id= 3
        else:
            deal.item_id= deal.item_id+1
        deal.save()
    imageurl = str(deal.item.image)
    deal.item.image = imageurl.replace("apps/items","",1)
    context = {'deal':deal}
    return render(request, 'items/index.html', context)

def browse(request, category):
    if category=='all':
        items = Items.objects.all().order_by('category').order_by('name')
    else:
        items = Items.objects.all().filter(category=category).order_by('name')

    for item in items:
        imageurl = str(item.image)
        item.image = imageurl.replace("apps/items","",1)

    context = {'items':items}
    return render(request, 'items/browse.html', context)

def create_deal(request):
    user = Users.objects.get(id=request.session['id'])
    if user.admin:
        return render(request, 'items/create_deal.html')
    return redirect('items:index')

def cart(request):
    if 'id' in request.session:
        user = Users.objects.get(id=request.session['id'])

        cart_items = Purchases.objects.filter(status='open').filter(user=user).prefetch_related('item')
        sum_total = 0.00
        rating = "1"

        for item in cart_items:
            sum_total = sum_total + float(item.item.price)
            imageurl = str(item.item.image)
            item.image = imageurl.replace("apps/items","",1)
        print sum_total
        form = CreditCardForm()

        if request.method == 'POST':
            if not cart_items:
                messages.error(request, 'No items to buy')
                return redirect('items:cart')
            form = CreditCardForm(request.POST)
            if form.is_valid():
                total_price = user.purchases_set.filter(status='open').aggregate(Sum('item__price')).get('item__price__sum') * 100
                charge_id = Purchases.chargeCard(int(total_price), request.POST['number'], request.POST['expiration_0'], request.POST['expiration_1'], request.POST['cvc'])
                if charge_id:
                    for item in user.purchases_set.filter(status='open'):
                        item.change_order_status(charge_id)
                    messages.success(request, 'Products purchased!')
                    send_email(user, cart_items)
                else:
                    messages.error(request, 'Card rejected')
                return redirect('items:cart')
        return render(request, 'items/cart.html', {'cart_items': cart_items, 'form': form, 'sum_total':sum_total})
    return redirect('users:index')

def remove_cart(request, id):
    if 'id' in request.session:
        delete = Purchases.objects.get(pk=id)
        delete.delete()
        return redirect('items:cart')
    return redirect('users:index')

def item(request, id):
    item = get_object_or_404(Items, id=id)
    discussion = Discussions.objects.filter(item_id=id).order_by('-created_at')
    items_left = Purchases.objects.filter(item_id=id).count()
    items_left = item.units - items_left
    imageurl = str(item.image)
    item.image = imageurl.replace("apps/items","",1)
    rating_avg = Ratings.objects.filter(item_id=item).aggregate(Avg('rating'))
    chart_max = 4
    chart_data =''
    hour = 0
    while hour<24:
        h = Purchases.objects.filter(item_id=id).filter(status='closed').filter(updated_at__hour=hour).count()
        if hour == 23:
            chart_data += str(h)
        else:
            chart_data += str(h)+','
        if int(h)> chart_max:
            chart_max = int(h)
        hour+=1
    print chart_data  
    try:
        r = Ratings.objects.get(user_id=request.session['id'],item_id=id)
    except:
        r = 0
    context = {'item': item, 'discussion': discussion,'items_left': items_left, 'rating_avg': rating_avg, 'r': r, 'chart_max':chart_max, 'chart_data':chart_data}
    return render(request, 'items/item.html', context)

def add_cart(request, id):
    try:
        quantity = int(request.POST['quantity'])
        item = id
        status = 'open'
        user = request.session['id']
        while quantity>0:
            Purchases.objects.create(item_id=item, user_id=user, status=status)
            quantity = quantity-1
        return redirect('/cart')
    except:
        return redirect('users:index')

def add_discussion(request):
    try:
         discussion = request.POST['discussion']
         user = request.session['id']
         item = request.POST['hidden_id']
         Discussions.objects.create(discussion=discussion, user_id=user, item_id=item)
         return redirect('items:item', id=item)
    except:
        return redirect('users:index')

def add_rating(request):
    try:
        rate = request.POST['rating']
        item = request.POST['hidden']
        user = request.session['id']
        try:
            r = Ratings.objects.get(user_id=user, item_id=item)
            Ratings.objects.filter(user_id=user).filter(item_id=item).update(rating=rate)
        except:
            Ratings.objects.create(item_id=item, user_id=user, rating=rate)
        return redirect('items:item', id=item)
    except:
        return redirect('users:index')

def add_item(request):
    if request.method == 'POST':
        Items.objects.add(request.POST['name'], request.POST['description'], request.POST['price'], request.POST['units'], request.POST['category'], request.FILES['image'])
    return redirect(reverse('items:create_deal'))

    #NEEDED TO ACCESS IMAGES FROM THIERE SAVED LOCATION
    # item = Items.objects.get(id=2)
    # imageurl = str(item.image)
    # item.image = imageurl.replace("apps/items","",1)
    # context = {'item':item, 'imageurl':imageurl}

#pip install django-chart-tools