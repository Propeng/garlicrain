from django.shortcuts import render
from django.http import JsonResponse, HttpResponseServerError
from .api import API
from . import rpc

api = API(rpc.get_session())

# Create your views here.
def balance(request):
	response = {'success': True, 'balance': api.balance}
	return JsonResponse(response)

def address(request):
	response = {'success': True, 'address': api.address}
	return JsonResponse(response)

def stats(request):
	response = {'success': True, 'address': api.address, 'balance': api.balance, 'payout': api.payout_amount, 'max_payout': api.max_payout, 'payout_ratio': api.payout_ratio}
	return JsonResponse(response)

def payout(request, address):
	#get user ip
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
		
	response = api.payout(address, ip)
	return JsonResponse(response)