from django.urls import path
from . import views
from  django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
    path('', views.index),  #the path for our index view
]
urlpatterns += staticfiles_urlpatterns()
