from django.db import models

# Create your models here.
class User(models.Model):
	address = models.CharField(max_length=35)
	ip = models.CharField(max_length=64)
	timestamp = models.DateTimeField()
	
	def __str__(self):
		return 'User IP %s address %s' % (self.ip, self.address)

class Log(models.Model):
	address = models.CharField(max_length=35)
	ip = models.CharField(max_length=64)
	payout = models.DecimalField(decimal_places=8, max_digits=12)
	prev_balance = models.DecimalField(decimal_places=8, max_digits=12)
	tx_id = models.CharField(max_length=64)
	timestamp = models.DateTimeField()
	
	def __str__(self):
		return 'Payout at %s' % self.timestamp

class LoyaltyLevel(models.Model):
	address = models.CharField(max_length=35)
	level = models.IntegerField()
	
	def __str__(self):
		return 'User %s level %d' % (self.address, self.level)