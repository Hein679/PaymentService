"""webapps2023 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from webapps2023 import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.redirect_to_webapps),
    path('webapps2023/', include('payment_service.urls')),
    path('currency_conversion/', include('currency_conversion.urls')),
    # re_path(r'^$', RedirectView.as_view(url='/webapps2023/login/', permanent=True)),
]