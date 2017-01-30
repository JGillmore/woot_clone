from __future__ import unicode_literals

from django.db import models
from ..loginapp.models import *

class ItemsManager(models.Manager):
	def validate(self, name, description, price, units, category, image):
		if name and description and price and units and category and image:
			return True
		return False

	def add(self, name, description, price, units, category, image):
		item = Items.objects.create(name=name, description=description, price=price, units=units, category=category, image=image)
		return

	def update(self):
		pass
	def delete(self):
		pass

class Items(models.Model):
	name = models.CharField(max_length=200)
	description = models.TextField()
	price = models.DecimalField(max_digits=9, decimal_places=2)
	units = models.PositiveSmallIntegerField()
	category = models.CharField(max_length=200)
	image = models.ImageField(upload_to='apps/wootapp/static/images/dbitems/')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = ItemsManager()

class CartsManager(models.Manager):
	def add(self):
		pass
	def delete(self):
		pass
	def checkout(self):
		pass

class Carts(models.Model):
	item = models.ForeignKey(Items, related_name='item_cart')
	user = models.ForeignKey(Users, related_name= 'user_cart')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = CartsManager()

class DisscussionsManager(models.Manager):
	def validate(self):
		pass
	def add(self):
		pass
	def update(self):
		pass
	def delete(self):
		pass

class Disscussions(models.Model):
	discussion = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(Users, related_name='user_discussion')
	item = models.ForeignKey(Items, related_name='item_discussion')
	objects = DisscussionsManager()

class RatingsManger(models.Manager):
	def validate(self):
		pass
	def add(self):
		pass
	def delete(self):
		pass
	def update(self):
		pass

class Ratings(models.Model):
	rating = models.PositiveSmallIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(Users, related_name='user_rating')
	item = models.ForeignKey(Items, related_name='item_rating')
	objects = RatingsManger()

class CCManager(models.Manager):
	def validate(self):
		pass
	def add(self):
		pass
	def update(self):
		pass
	def delete():
		pass

class CC(models.Model):
	full_name = models.CharField(max_length=100)
	card_number = models.IntegerField()
	expiration_date = models.DateField()
	security_code = models.PositiveSmallIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(Users, related_name='user_cc')
	objects = CCManager()
