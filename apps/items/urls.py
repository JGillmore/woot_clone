from django.conf.urls import url
from views import *

urlpatterns = [
	url(r'^$', index, name='index'),
	url(r'^browse/(?P<category>.+$)', browse, name='browse'),
	url(r'^create$', create_deal, name='create_deal'),
	url(r'^add$', add_item, name='add_item'),
	url(r'^item/(?P<id>\d+$)', item, name='item'),
	url(r'^cart$', cart, name='cart'),
	url(r'^add_rating$', add_rating),
]
