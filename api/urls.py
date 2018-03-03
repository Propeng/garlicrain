from django.urls import path

from . import views

urlpatterns = [
	path('balance', views.balance),
	path('address', views.address),
	path('stats', views.stats),
	#path('payout/<address>', views.payout),
]
