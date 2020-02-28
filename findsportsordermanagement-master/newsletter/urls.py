from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('changenewsletter', views.index, name='changenewsletter'),
    path('shownewsletter', views.shownewsletter, name='shownewsletter'),
    path('newsletterecommender', views.get_recommended_products, name='shownewsletter'),
]
