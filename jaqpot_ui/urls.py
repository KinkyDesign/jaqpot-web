from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from jaqpot_ui import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='home'),
                       url(r'^login', views.login),
                       url(r'^logout', views.logout),

                       # Administration page
                       url(r'^admin/', include(admin.site.urls)),
)
