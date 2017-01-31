from django.conf.urls import url

from views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^login$',login, name='login'),
    url(r'^register$',register, name='register'),
    url(r'^logout$',logout, name='logout'),
    url(r'^profile$', profile, name='profile'),
    url(r'^update_info$', update_info, name='update_info'),
]
