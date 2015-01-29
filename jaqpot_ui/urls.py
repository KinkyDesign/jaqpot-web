from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from jaqpot_ui import views

urlpatterns = patterns('',
    url(r'^$', views.WelcomePage, name='home'),
    url(r'^send', views.Login),
    url(r'^actions', views.CheckUser),

    # Authentication module
    #url(r'^account/', include('allauth.urls')),

    # Administration page
    url(r'^admin/', include(admin.site.urls)),


)
