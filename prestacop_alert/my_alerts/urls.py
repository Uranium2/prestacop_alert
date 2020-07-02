from django.urls import path
from my_alerts import views

urlpatterns = [
    path('', views.index, name='index'),
]