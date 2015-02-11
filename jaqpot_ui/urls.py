from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from jaqpot_ui import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='home'),
                       url(r'^login', views.login),
                       url(r'^logout', views.logout),
                       url(r'^task', views.task),
                       url(r'^t_detail', views.taskdetail),
                       url(r'^bibtex', views.bibtex),
                       url(r'^bib_detail', views.bib_detail),
                       url(r'^add_bibtex', views.add_bibtex),
                       url(r'^sub', views.sub),
                       url(r'^user', views.user),
                       url(r'^train', views.trainmodel),
                       url(r'^dataset', views.choose_dataset),


                       # Administration page
                       url(r'^admin/', include(admin.site.urls)),
)
