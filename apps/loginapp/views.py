from django.shortcuts import render, redirect
from .models import Users
from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse
from datetime import date


def index(request):
    context = {}
    if messages:
        context['messages']=get_messages(request)
    return render(request, 'loginapp/index.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if Users.objects.login(request,email,password):
            request.session['today']=date.today().strftime('%b %d, %Y')
            request.session['restrictday']=str(date.today())
            return redirect(reverse('blackbelt:index'))
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
            return redirect(reverse('blackbelt:index'))
        return redirect('/')
