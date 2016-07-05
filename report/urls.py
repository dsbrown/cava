from django.conf.urls import url,include
from report.views import VehicleList, ModelList, index, vehicles, market, settings, MakeCreate, MakeUpdate, MakeDelete, ModelCreate, ModelUpdate, ModelDelete
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^market/', views.market, name='market'),
    url(r'^vehicles/$', views.vehicles, name='vehicles'),
    url(r'^vehicles/list/$', VehicleList.as_view(), name='VehicleList'),   
    url(r'^model/list/([\w-]+)/$', ModelList.as_view(), name='ModelList'),     
    url(r'^settings$', views.settings, name='settings'), 
    url(r'make/add/$', MakeCreate.as_view(), name='make-add'),
    url(r'make/(?P<make>.+?)/$', MakeUpdate.as_view(), name='make-update'),
    url(r'make/(?P<make>.+?)/delete/$', MakeDelete.as_view(), name='make-delete'),
    url(r'model/add/$', ModelCreate.as_view(), name='model-add'),
    url(r'model/(?P<make>.+?)/(?P<model>.+?)/(?P<year>.+?)/$', ModelUpdate.as_view(), name='model-update'),
    url(r'model/(?P<make>.+?)/(?P<model>.+?)/(?P<year>.+?)/delete/$', ModelDelete.as_view(), name='model-delete'),
]
