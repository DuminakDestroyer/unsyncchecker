from django.conf.urls import url
from . import views

urlpatterns =[
	url(r'^$', views.home, name="home"),
	url('home', views.home, name='home'),
	url('dashboard', views.dashboard, name='dashboard'),
	url('logout', views.logout_view, name='logout'),
	url('unbar', views.unbar, name='unbar'),
	url('report', views.report, name='report'),
]