from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='main'),
	path('history', views.history, name='history'),
	path('loyalty', views.loyalty, name='loyalty'),
]
