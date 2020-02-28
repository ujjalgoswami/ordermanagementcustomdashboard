"""findsportsordermanagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.utils.functional import curry
from django.views.defaults import *

urlpatterns = [
    path('', include('home.urls')),
    path('products/', include('products.urls')),
    path('stocklevel/', include('stocklevel.urls')),
    path('netoapihook/', include('netoapihook.urls')),
    path('automation/', include('automation.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('customers/', include('customers.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('orders/', include('orders.urls')),
    path('trackingid/', include('trackingid.urls')),
    path('purchaseorder/', include('purchaseorder.urls')),
    path('zendesk/', include('zendesk.urls')),
    path('warehouse/', include('warehouse.urls')),
    path('refunds/', include('refunds.urls')),
    path('newsletter/', include('newsletter.urls')),
    path('usermanual/', include('usermanual.urls')),
    path('login/', include('login.urls')),
    path('testfeatures/', include('testfeatures.urls')),
    path('stockupdate/', include('stockupdate.urls')),
    path('timebomb/', include('timebomb.urls')),
    path('escalatedorders/', include('escalatedorders.urls')),
    path('customerservice/', include('customerservice.urls')),
    path('categorization/', include('categorization.urls')),
    path('tasklist/', include('tasklist.urls')),
    path('admin/', admin.site.urls),
]



handler500 = curry(server_error, template_name='500error/500error.html')