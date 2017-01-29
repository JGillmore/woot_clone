from django.conf.urls import url
from views import *

urlpatterns = [
	url(r'^$', index, name='index'),
	url(r'^user$', user, name='user'),
	url(r'^browse/(?P<category>.+$)', browse, name='browse'),
	url(r'^create$', create_deal, name='create_deal'),
	url(r'^item/(?P<id>\d+$)', item, name='item'),
	url(r'^cart$', cart, name='cart'),
	url(r'^checkout$', checkout, name='checkout'),
]
