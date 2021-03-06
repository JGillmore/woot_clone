from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Avg, Sum, Count
from django.contrib import messages
from django.template.loader import get_template
from django.views.generic import ListView
from django.core.mail import EmailMessage, send_mail
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.http import HttpResponse
from forms import CreditCardForm, NewItemForm
from .models import *
from ..users.models import Users
from .models import Items, Purchases, Discussions
import datetime
import json
from django.http import HttpResponseRedirect

def logged_in(function):
    def wrap(request, *args, **kwargs):
        if 'id' in request.session:
            return function(request, *args, **kwargs)
        else:
            return redirect('users:index')

    wrap.__doc__=function.__doc__
    wrap.__name__=function.__name__
    return wrap

def send_email(user, cart):
    template = get_template('contact_template.txt')
    content = template.render({'first_name': user.first_name, 'purchases': cart})
    email = EmailMessage("Your order",	content, "Woot", [user.email], headers = {'Reply-To': 'wootclone.dojo@gmail.com'})
    email.send()

def home(request):
    deal = DealofTheMinute.objects.get(id=1)
    time_diff = datetime.datetime.utcnow().replace(tzinfo=None) - deal.updated_at.replace(tzinfo=None)
    if int(time_diff.total_seconds()) > 30:
        if deal.item_id == 19:
            deal.item_id= 3
        else:
            deal.item_id= deal.item_id+1
        deal.save()
    imageurl = str(deal.item.image)
    deal.item.image = imageurl.replace("apps/items","",1)
    categories = Items.objects.all().order_by('category').values_list('category', flat=True).distinct()

    data = [['Category', 'Items']]
    for c in categories:
        count = Purchases.objects.filter(status='closed').filter(item_id__category=c).count()
        data.append([str(c),count])

    context = {'categories':categories,'deal':deal, 'data':json.dumps(data)}
    return render(request, 'items/home.html', context)


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

@logged_in
def create_deal(request):
    try:
        user = Users.objects.get(id=request.session['id'])
    except:
        return redirect('items:home')
    users = Users.objects.filter(admin=0).order_by('email')
    if user.admin:
        form = NewItemForm()
        categories = Items.objects.all().order_by('category').values_list('category', flat=True).distinct()
        return render(request, 'items/create_deal.html', {'categories':categories, 'form': form, 'users':users})
    return redirect('items:home')

@logged_in
def promote(request, id):
    user = Users.objects.get(id=request.session['id'])
    if user.admin:
        u = Users.objects.filter(id=id).update(admin=1)
        return redirect('/create')
    return redirect('items:home')

@logged_in
def add_item(request):
    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item added')
            return redirect('users:profile')
    return render(request, 'items/create_deal.html', {'form': form})

@logged_in
def cart(request):
    user = Users.objects.get(id=request.session['id'])
    cart_items = Purchases.objects.filter(status='open').filter(user=user).prefetch_related('item')
    sum_total = 0.00
    rating = "1"
    all_items = Items.objects.all()
    for item in all_items:
        imageurl = str(item.image)
        item.image = imageurl.replace("apps/items","",1)

    for item in cart_items:
        sum_total = sum_total + float(item.item.price)

    unique_cart = Purchases.objects.filter(status='open').values('item_id').annotate(the_count=Count('item_id'))
    unique_items = Purchases.objects.filter(status='open').filter(user=user).values_list('item_id', flat=True).distinct()

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
    return render(request, 'items/cart.html', {'cart_items': cart_items, 'form': form, 'sum_total':sum_total, 'categories':categories, 'unique_cart':unique_cart, 'unique_items':unique_items, 'all_items':all_items})
    return redirect('users:index')

@logged_in
def remove_cart_unit(request, id):
    delete = Purchases.objects.filter(user_id=request.session['id']).filter(status='open').filter(item_id=id)
    delete.delete()
    return redirect('items:cart')

@logged_in
def increase_cart_quantity(request, id):
    status = 'open'
    user = request.session['id']
    quantity = Purchases.objects.filter(item_id=id).filter(status='open').filter(user_id=user).count()
    quantity= quantity +1
    items_left = Purchases.objects.filter(item_id=id).filter(status='closed').count()
    item = Items.objects.get(pk=id)
    items_left = item.units - items_left
    if quantity > items_left:
        messages.add_message(request, messages.ERROR, 'Not enough units remaining')
        return redirect('items:cart')
    Purchases.objects.create(item_id=id, user_id=user, status=status)
    return redirect('items:cart')

@logged_in
def decrease_cart_quantity(request, id):
    user = request.session['id']
    quantity = Purchases.objects.filter(item_id=id).filter(user_id=user).filter(status='open').count()
    if quantity == 0:
        messages.add_message(request, messages.ERROR, 'Cannot delete you do not have this item in your cart')
        return redirect('items:cart')
    decrease = Purchases.objects.filter(item_id=id).filter(user_id=user).filter(status='open').first()
    decrease.delete()
    return redirect('items:cart')

@logged_in
def remove_cart_all(request):
    delete = Purchases.objects.filter(status='open').filter(user_id=request.session['id'])
    delete.delete()
    return redirect('items:cart')

def item(request, id):
    try:
        item = Items.objects.get(id=id)
    except:
        return redirect(reverse('items:home'))
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
        item_rating_by_user = Ratings.objects.filter(user_id=request.session['id']).filter(item_id=id)
    except:
        item_rating_by_user = ''
    else:
        if item_rating_by_user:
            item_rating_by_user = item_rating_by_user[0]

    categories = Items.objects.all().order_by('category').values_list('category', flat=True).distinct()
    context = {'categories':categories, 'item': item, 'discussion': discussion,'items_left': items_left, 'rating_avg': rating_avg, 'r': item_rating_by_user, 'chart_data':json.dumps(chart_data)}
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

@logged_in
def add_cart(request, id):
    try:
        quantity = int(request.POST['quantity'])
        status = 'open'
        user = request.session['id']
        user_o = Users.objects.get(id=user)
        items_sold = Purchases.objects.filter(item_id=id).filter(status='closed').count()
        item = Items.objects.get(pk=id)
        items_left = item.units - items_sold
        if request.is_ajax():
            if Purchases.objects.filter(item_id=id).filter(status='open').filter(user_id=user).count() > items_left:
                return HttpResponse('FALSE')
            else:
                Purchases.objects.create(item_id=id, user_id=user, status=status)
                return HttpResponse('TRUE')
        if quantity > items_left:
            messages.add_message(request, messages.ERROR, 'Not enough units remaining, please select a lower quantity')
            return redirect('/item/'+id)
        while quantity>0:
            Purchases.objects.create(item_id=id, user_id=user, status=status)
            quantity = quantity-1
        return redirect('/cart')
    except:
        return redirect('users:index')

@logged_in
def add_discussion(request):
    try:
         discussion = request.POST['discussion']
         user = request.session['id']
         item = request.POST['hidden_id']
         Discussions.objects.create(discussion=discussion, user_id=user, item_id=item)
         return redirect('items:item', id=item)
    except:
        return redirect('users:index')

@logged_in
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
