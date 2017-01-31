from django.shortcuts import render, redirect
from .models import Users
from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from datetime import date

def index(request):
    context = {}
    request.session['restrictday']=str(date.today())
    if messages:
        context['messages']=get_messages(request)
    return render(request, 'loginapp/index.html', context)

def user(request):
    if 'id' in request.session:
        user = Users.objects.get(id=request.session['id'])
        purchased_items = Items.objects.filter(item_purchased__status='closed').filter(item_purchased__user=user)
        birth_date = str(user.birth_date)
        context = {'user':user, 'birth_date':birth_date, 'purchased_items':purchased_items}
        return render(request, 'wootapp/user.html', context)
    return redirect('login:login')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if Users.objects.login(request,email,password):
            request.session['today']=date.today().strftime('%b %d, %Y')
            request.session['restrictday']=str(date.today())
            return redirect(reverse('woot:index'))
    return redirect('/')

def logout(request):
    request.session.clear()
    return redirect('/')

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
            return redirect(reverse('woot:index'))
        return redirect('/')

def update_info(request):
    if request.method=='POST':
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        birth_date = request.POST['birth_date']
        Users.objects.update_info(request, email, first_name, last_name, birth_date)
    return redirect(reverse('woot:user'))
