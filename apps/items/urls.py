from django.conf.urls import url
from views import *

from .views import BrowseView

urlpatterns = [
	url(r'^$', home, name='home'),
	url(r'^browse/(?P<category>.+$)', BrowseView.as_view(), name='browse'),
	url(r'^create$', create_deal, name='create_deal'),
	url(r'^add$', add_item, name='add_item'),
	url(r'^item/(?P<id>\d+$)', item, name='item'),
	url(r'^cart$', cart, name='cart'),
	url(r'^add_rating$', add_rating),
	url(r'^add_discussion$', add_discussion),
	url(r'^add_cart/(?P<id>\d+$)', add_cart),
	url(r'^remove_cart_unit/(?P<id>\d+$)', remove_cart_unit),
	url(r'^chart_data/(?P<id>\d+$)', chart_data),
	url(r'^remove_cart/all$', remove_cart_all),
	url(r'^promote/(?P<id>\d+$)', promote),
	url(r'^increase/(?P<id>\d+$)', increase_cart_quantity),
	url(r'^decrease/(?P<id>\d+$)', decrease_cart_quantity),
]
