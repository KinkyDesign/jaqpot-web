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
                       url(r'^data_detail', views.dataset_detail),
                       url(r'^data', views.dataset),
                       url(r'^algorithm_detail', views.algorithm_detail),
                       url(r'^algorithm', views.algorithm),
                       url(r'^alg', views.alg),
                       url(r'^conformer', views.conformer),
                       url(r'^model', views.model),
                       url(r'^m_detail', views.model_detail),
                       url(r'^feature_details', views.features),
                       url(r'^features', views.features),
                       url(r'^predict_model', views.predict_model),
                       url(r'^predict', views.predict),


                       # Administration page
                       url(r'^admin/', include(admin.site.urls)),
)
