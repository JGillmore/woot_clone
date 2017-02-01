from __future__ import unicode_literals

from django.db import models
from ..users.models import *
import settings

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
	image = models.ImageField(upload_to='apps/items/static/images/dbitems/')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = ItemsManager()

class Purchases(models.Model):
	def __init__(self, *args, **kwargs):
		super(Purchases, self).__init__(*args, **kwargs)

		import stripe
		stripe.api_key = settings.STRIPE_API_KEY

		self.stripe = stripe
		# HEY GUYS! pip install --index-url https://code.stripe.com --upgrade stripe

	item = models.ForeignKey(Items, related_name='item_purchased')
	user = models.ForeignKey(Users)
	status = models.CharField(max_length=255)
	charge_id = models.CharField(max_length=32, default='')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def charge(self, price_in_cents, number, exp_month, exp_year, cvc):
		# Takes a the price and credit card details: number, exp_month, exp_year, cvc. Returns a tuple: (Boolean, Class) where the boolean is if the charge was successful, and the class is response (or error) instance.
		if self.charge_id: # don't let this be charged twice!
			return False, Exception(message="Already charged.")

		try:
		  	response = self.stripe.Charge.create(
			amount = price_in_cents,
			currency = "usd",
			card = {
			  "number" : number,
			  "exp_month" : exp_month,
			  "exp_year" : exp_year,
			  "cvc" : cvc,

			  #### it is recommended to include the address!
			  #"address_line1" : self.address1,
			  #"address_line2" : self.address2,
			  #"address_zip" : self.zip_code,
			  #"address_state" : self.state,
			},
			description='Thank you for your purchase!')

			self.charge_id = response.id

		except self.stripe.CardError, ce:
			print ce
			return False, ce

		self.status = 'closed'
		self.save()
		return True, response

class DiscussionsManager(models.Manager):
	def validate(self):
		pass
	def add(self):
		pass
	def update(self):
		pass
	def delete(self):
		pass

class Discussions(models.Model):
	discussion = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(Users, related_name='user_discussion')
	item = models.ForeignKey(Items, related_name='item_discussion')
	objects = DiscussionsManager()

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

class DealofTheMinute(models.Model):
	updated_at = models.DateTimeField(auto_now=True)
	item = models.ForeignKey(Items)
