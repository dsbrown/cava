from django.conf.urls import url,include
from report.views import VehicleList, ModelList, index, vehicles, market, settings
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^market/', views.market, name='market'),
    url(r'^vehicles/$', views.vehicles, name='vehicles'),
    url(r'^vehicles/list/$', VehicleList.as_view(), name='VehicleList'),   
    url(r'^model/list/([\w-]+)/$', ModelList.as_view(), name='ModelList'),     
    url(r'^settings$', views.settings, name='settings'), 
]
