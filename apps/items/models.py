from __future__ import unicode_literals

from django.db import models
from ..users.models import *
import settings
import stripe

stripe.api_key = settings.STRIPE_API_KEY

class Items(models.Model):
	name = models.CharField(blank=False, max_length=200)
	description = models.TextField(blank=False,)
	price = models.DecimalField(blank=False, max_digits=9, decimal_places=2)
	units = models.PositiveSmallIntegerField(blank=False)
	available = models.BooleanField(default=True)
	category = models.CharField(blank=False, max_length=200)
	image = models.ImageField(blank=False, upload_to='apps/items/static/images/dbitems/')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class Purchases(models.Model):
	item = models.ForeignKey(Items, related_name='item_purchased')
	user = models.ForeignKey(Users)
	status = models.CharField(max_length=255)
	charge_id = models.CharField(max_length=32, default='')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	@classmethod
	def chargeCard(cls, price_in_cents, number, exp_month, exp_year, cvc):
		try:
		  	response = stripe.Charge.create(
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

			charge_id = response.id
			return charge_id

		except stripe.CardError, ce:
			return False

	def change_order_status(self, charge_id):
		# Takes a the price and credit card details: number, exp_month, exp_year, cvc. Returns a tuple: (Boolean, Class) where the boolean is if the charge was successful, and the class is response (or error) instance.
		if self.charge_id: # don't let this be charged twice!
			return False, Exception(message="Already charged.")

		self.charge_id = charge_id
		self.status = 'closed'
		self.save()
		return True

	def send_email(self):
	        template = get_template('contact_template.txt')
	        context = Context(self.cleaned_data)
	        content = template.render(context)
	        email = EmailMessage(
	            "New contact form submission",
	            content,
	            "Your website" +'',
	            [''], #Your email account
	            headers = {'Reply-To': self.cleaned_data['email'] }
	        )
	        email.send()

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
