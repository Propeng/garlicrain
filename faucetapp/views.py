from django.shortcuts import render
from api import rpc
import api.views
from faucet.faucet_settings import faucet_settings
from api.api import API
from api.models import Log, LoyaltyLevel
import urllib.request
import urllib.parse
import json

api = API(rpc.get_session())

# Create your views here.
def index(request):
	params = {'faucet_settings': faucet_settings}
	payout_address = request.POST.get('payout_address')
	if payout_address:
		#get user ip
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
			
		#verify captcha
		if faucet_settings['use_recaptcha']:
			captcha = request.POST.get('g-recaptcha-response', '')
			verify_post = [('secret', faucet_settings['recaptcha_secret']), ('response', captcha), ('remoteip', ip)]
			verify_result = urllib.request.urlopen('https://www.google.com/recaptcha/api/siteverify', urllib.parse.urlencode(verify_post).encode('utf-8'))
			verify_data = json.loads(verify_result.read().decode('utf-8'))
		
		if not faucet_settings['use_recaptcha'] or verify_data['success']:
			tx_result = api.payout(payout_address, ip)
			if tx_result['success']:
				params['success'] = True
				params['message'] = 'Sent %s %s to %s!<br />Transaction ID: %s' % (tx_result['amount'], faucet_settings['coin_symbol'], tx_result['address'], tx_result['tx_id'])
				if tx_result['loyalty_multiplier'] > 1:
					params['message'] = ('<b>Loyalty perk activated! Payout multiplier: %sx</b><br />' % tx_result['loyalty_multiplier']) + params['message']
			else:
				params['error'] = True
				params['message'] = tx_result['message']
		else:
			params['error'] = True
			params['message'] = 'Incorrect captcha.'
	
	balance = api.balance
	address = api.address
	payout = api.format_amount(api.payout_amount)
	params.update({'balance': balance, 'address': address, 'payout': payout, 'max_payout': api.max_payout, 'payout_percent': api.payout_ratio*100, 'payout_formula': api.payout_formula})
	
	return render(request, 'faucetapp/index.html', params)

def loyalty(request):
	count = 10
	leaderboard = list(LoyaltyLevel.objects.all().order_by('-level')[:count])
	params = {'faucet_settings': faucet_settings, 'count': count, 'leaderboard': leaderboard}
	
	payout_address = request.POST.get('payout_address')
	if payout_address:
		try:
			loyalty = LoyaltyLevel.objects.get(address=payout_address)
			params['success'] = True
			params['message'] = 'Your current loyalty level is <b>%d</b><br />Payout multiplier: <b>%sx</b>' % (loyalty.level, api.get_loyalty_multiplier(loyalty.level))
		except LoyaltyLevel.DoesNotExist:
			params['error'] = True
			params['message'] = 'Address not found.'
	
	return render(request, 'faucetapp/loyalty.html', params)

def history(request):
	count = 20
	records = list(Log.objects.all().order_by('-timestamp')[:count])
	params = {'faucet_settings': faucet_settings, 'count': count, 'records': records}
	return render(request, 'faucetapp/history.html', params)