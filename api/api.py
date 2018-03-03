from faucet.faucet_settings import faucet_settings
from .models import User, Log, LoyaltyLevel
from datetime import datetime, timedelta
import pytz
from decimal import Decimal
import math

class API:
	def __init__(self, rpc):
		self.rpc = rpc
		self.account = faucet_settings['account_name']
	
	@property
	def balance(self):
		return self.rpc.getbalance(self.account)
	
	@property
	def address(self):
		return self.rpc.getaccountaddress(self.account)
	
	def payout(self, address, ip):
		#check db for previous payouts by this user
		query = User.objects.filter(address=address) | User.objects.filter(ip=ip)
		
		if len(query) == 0:
			#new user
			user_entry = User()
		else:
			#existing user. check if enough time has passed since last payout
			user_entry = query.order_by('-timestamp')[0]
			time_diff = datetime.utcnow().replace(tzinfo=pytz.UTC) - user_entry.timestamp
			if time_diff < timedelta(hours=8):
				time_remaining = timedelta(hours=8) - time_diff
				time_split = str(time_remaining).split('.')[0].split(':')
				time_split.reverse()
				time_str = "%ssec" % time_split[0]
				if len(time_split) > 1 and int(time_split[1]) > 0:
					time_str = ("%smin " % time_split[1]) + time_str
				if len(time_split) > 2 and int(time_split[2]) > 0:
					time_str = ("%shr " % time_split[2]) + time_str
				response = {'success': False, 'message': 'Please wait %s until your next payout.' % time_str}
				return response
		
		#user has permissions for payout
		#check address validity
		if not self.rpc.validateaddress(address)['isvalid']:
			response = {'success': False, 'message': 'Address is invalid.'}
			return response
		
		#get payout amount and check if it is 0 (faucet empty)
		payout = self.payout_amount
		if payout == 0:
			response = {'success': False, 'message': 'Faucet is empty :('}
			return response
			
		#get loyalty perk
		try:
			loyalty = LoyaltyLevel.objects.get(address=address)
		except LoyaltyLevel.DoesNotExist:
			loyalty = LoyaltyLevel(address=address, level=0)
		multiplier = self.get_loyalty_multiplier(loyalty.level+1)
		
		#all good. do the payout
		balance = self.balance
		payout_formatted = self.format_amount(payout*multiplier)
		try:
			tx_id = self.rpc.sendfrom(self.account, address, payout_formatted)
		except Exception:
			response = {'success': False, 'message': 'Transaction failed, faucet balance is probably too low'}
			return response
		
		loyalty.level += 1
		loyalty.save()
		
		user_entry.address = address
		user_entry.ip = ip
		user_entry.timestamp = datetime.utcnow().replace(tzinfo=pytz.UTC)
		user_entry.save()
		
		log_entry = Log(address = address, ip = ip, payout = Decimal(payout_formatted), timestamp = user_entry.timestamp, tx_id = tx_id, prev_balance = Decimal(balance))
		log_entry.save()
		
		response = {'success': True, 'address': address, 'amount': payout_formatted, 'tx_id': tx_id, 'loyalty_level': loyalty.level, 'loyalty_multiplier': multiplier}
		return response
	
	def get_loyalty_multiplier(self, level):
		if faucet_settings['use_loyalty_perks']:
			multiplier = 1 + 0.5*(level // 5)
			if multiplier > 2:
				multiplier = 2
			return multiplier
		else:
			return 1
	
	@property
	def max_payout(self):
		return 0#0.005
	
	@property
	def payout_ratio(self):
		return 0#0.002
	
	@property
	def payout_amount(self):
		#payout = self.payout_ratio * self.balance
		#if payout < 0.00000001:
		#	return 0
		#if payout > self.max_payout:
		#	payout = self.max_payout
		payout = 0.0012*math.sqrt(self.balance)
		return payout
	
	@property
	def payout_formula(self):
		return "0.0012*sqrt(balance)"

	def format_amount(self, amount):
		split = str(amount).split('.')
		split[1] = split[1][:8]
		return split[0] + '.' + split[1]