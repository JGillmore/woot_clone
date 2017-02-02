from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Avg, Sum
from django.contrib import messages
from django.template.loader import get_template
from django.views.generic import ListView
from django.core.mail import EmailMessage, send_mail
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.http import HttpResponse
from forms import CreditCardForm
from .models import *
from ..users.models import Users
from .models import Items, Purchases, Discussions
import datetime
import json
from sys import platform


def send_email(user, cart):
    template = get_template('contact_template.txt')
    content = template.render({'first_name': user.first_name, 'purchases': cart})
    # That email you see below, is suppoed to be the customer's email
    email = EmailMessage("Your order",	content, "Woot", [user.email], headers = {'Reply-To': 'wootclone.dojo@gmail.com'})
    email.send()

def home(request):
    if platform == 'win32':
        time = -21570
    else:
        time = 30
    deal = DealofTheMinute.objects.get(id=1)
    time_diff = datetime.datetime.now().replace(tzinfo=None) - deal.updated_at.replace(tzinfo=None)
    if int(time_diff.total_seconds()) > time:
        if deal.item_id == 18:
            deal.item_id= 3
        else:
            deal.item_id= deal.item_id+1
        deal.save()
    imageurl = str(deal.item.image)
    deal.item.image = imageurl.replace("apps/items","",1)
    categories = Items.objects.all().order_by('category').values_list('category', flat=True).distinct()
    context = {'categories':categories,'deal':deal}
    return render(request, 'items/index.html', context)

class BrowseView(ListView):
    model = Items
    template_name = 'items/browse.html'
    context_object_name = "items"
    paginate_by = 12

    def get_queryset(self):
        if self.kwargs['category']=='all':
            queryset = Items.objects.all().order_by('category', 'name')
        else:
            queryset = Items.objects.all().filter(category=self.kwargs['category']).order_by('name')

        for item in queryset:
            imageurl = str(item.image)
            item.image = imageurl.replace("apps/items","",1)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(BrowseView, self).get_context_data(**kwargs)
        context['category'] = self.kwargs['category']
        categories = Items.objects.all().order_by('category').values_list('category', flat=True).distinct()
        context['categories'] = Items.objects.all().order_by('category').values_list('category', flat=True).distinct()
        return context

def create_deal(request):
    user = Users.objects.get(id=request.session['id'])
    if user.admin:
        categories = Items.objects.all().order_by('category').values_list('category', flat=True).distinct()
        context = {'categories':categories}
        return render(request, 'items/create_deal.html', context)
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
        categories = Items.objects.all().order_by('category').values_list('category', flat=True).distinct()
        return render(request, 'items/cart.html', {'cart_items': cart_items, 'form': form, 'sum_total':sum_total, 'categories':categories})
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
    items_left = Purchases.objects.filter(item_id=id).filter(status='closed').count()
    items_left = item.units - items_left
    imageurl = str(item.image)
    item.image = imageurl.replace("apps/items","",1)
    rating_avg = Ratings.objects.filter(item_id=item).aggregate(Avg('rating'))
    chart_data =[['Hour', 'Items Sold']]
    hour = 0
    while hour<24:
        time = ['12am','1am','2am','3am','4am','5am','6am','7am','8am','9am','10am','11am','12pm','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm']
        h = Purchases.objects.filter(item_id=id).filter(status='closed').filter(updated_at__hour=hour).count()
        chart_data.append([time[hour],h])
        hour+=1
    try:
        r = Ratings.objects.get(user_id=request.session['id'],item_id=id)
    except:
        r = 0
    context = {'item': item, 'discussion': discussion,'items_left': items_left, 'rating_avg': rating_avg, 'r': r, 'chart_data':json.dumps(chart_data)}
    return render(request, 'items/item.html', context)

def chart_data(request, id):
    chart_data =[['Hour', 'Items Sold']]
    hour = 0
    while hour<24:
        time = ['12am','1am','2am','3am','4am','5am','6am','7am','8am','9am','10am','11am','12pm','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm']
        h = Purchases.objects.filter(item_id=id).filter(status='closed').filter(updated_at__hour=hour).count()
        chart_data.append([time[hour],h])
        hour+=1
    chart_data = json.dumps(chart_data)
    return HttpResponse(chart_data)

def add_cart(request, id):
    try:
        quantity = int(request.POST['quantity'])
        item = id
        status = 'open'
        user = request.session['id']
        items_left = Purchases.objects.filter(item_id=id).filter(status='closed').count()
        items_left = item.units - items_left
        if quantity > items_left:
            messages.add_message(request, messages.ERROR, 'Not enough units remaining, please select a lower quantity')
            return redirect('/item/'+id)
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

@csrf_exempt
def add_rating(request):
    rate = request.POST['rating']
    item = request.POST['hidden']
    user = request.session['id']

    if rate and item and user:
        try:
            Ratings.objects.create(item_id=item, user_id=user, rating=rate)
        except:
            return HttpResponse('Failed rating submission')
        else:
            return HttpResponse('Successful rating submission')
    else:
        return HttpResponse('Failed rating submission')

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
