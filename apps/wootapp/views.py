from django.shortcuts import render

def index(request):
    return render(request, 'wootapp/index.html')
def user(request):
    return render(request, 'wootapp/user.html')
def browse(request):
    return render(request, 'wootapp/browse.html')
def create_deal(request):
    return render(request, 'wootapp/create_deal.html')
def cart(request):
    return render(request, 'wootapp/cart.html')
def item(request):
    return render(request, 'wootapp/item.html')
def checkout(request):
    return render(request, 'wootapp/checkout.html')
