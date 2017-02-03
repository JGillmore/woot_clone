from django.shortcuts import render, redirect
from .models import Users
from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from datetime import date
from django.db.models import Count
from django.http import HttpResponseRedirect

from ..items.models import Items, Purchases, Discussions
from .models import Users

def logged_in(function):
    def wrap(request, *args, **kwargs):
        if 'id' in request.session:
            return function(request, *args, **kwargs)
        else:
            return redirect('users:index')

    wrap.__doc__=function.__doc__
    wrap.__name__=function.__name__
    return wrap

def index(request):
    categories = Items.objects.all().order_by('category').values_list('category', flat=True).distinct()
    context = {'categories':categories}
    request.session['restrictday']=str(date.today())
    if messages:
        context['messages']=get_messages(request)
    return render(request, 'users/index.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if Users.objects.login(request,email,password):
            request.session['today']=date.today().strftime('%b %d, %Y')
            request.session['restrictday']=str(date.today())
            messages.success(request, 'Login successful')
            return redirect(reverse('items:home'))
    return redirect('users:index')

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirmpassword = request.POST['confirmpassword']
        birth_date=request.POST['birth_date']
        temp = Users.objects.register(request,first_name,last_name,email,password,confirmpassword, birth_date)
        if temp:
            request.session['name']=temp.first_name
            request.session['id']=temp.id
            request.session['today']=date.today().strftime('%b %d, %Y')
            request.session['restrictday']=str(date.today())
            return redirect(reverse('items:home'))
    return redirect('users:index')

@logged_in
def logout(request):
    request.session.clear()
    return redirect('users:login')

@logged_in
def profile(request):
    if 'id' in request.session:
        user = Users.objects.get(id=request.session['id'])
        comments = Discussions.objects.filter(user=user).order_by('-created_at')
        user = Users.objects.get(id=request.session['id'])
        purchased_items = Purchases.objects.filter(status='closed').filter(user=user).order_by('-created_at')
        all_items = Items.objects.all()

        for item in all_items:
            imageurl = str(item.image)
            item.image = imageurl.replace("apps/items","",1)
        
        unique_cart = Purchases.objects.filter(status='closed').filter(user_id=user).values('item_id').annotate(the_count=Count('item_id'))
        unique_items = Purchases.objects.filter(status='closed').filter(user_id=user).values_list('item_id', flat=True).distinct()
        birth_date = str(user.birth_date)
        categories = Items.objects.all().order_by('category').values_list('category', flat=True).distinct()
        context = {'categories':categories, 'comments':comments, 'user':user, 'birth_date':birth_date, 'purchased_items':purchased_items, 'all_items':all_items, 'unique_cart':unique_cart, 'unique_items':unique_items}
        return render(request, 'users/profile.html', context)
    return redirect('users:login')

@logged_in
def update_info(request):
    if request.method=='POST':
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        birth_date = request.POST['birth_date']
        Users.objects.update_info(request, email, first_name, last_name, birth_date)
    return redirect('users:profile')
