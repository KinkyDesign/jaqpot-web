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
                       url(r'^bibtex_delete', views.bib_delete),
                       url(r'^bibtex', views.bibtex),
                       url(r'^bib_detail', views.bib_detail),
                       url(r'^add_bibtex', views.add_bibtex),
                       url(r'^bibtex_delete', views.bib_delete),
                       url(r'^sub', views.sub),
                       url(r'^user', views.user),
                       url(r'^train', views.trainmodel),
                       url(r'^dataset', views.choose_dataset),
                       url(r'^data_detail', views.dataset_detail),
                       url(r'^data', views.dataset),
                       url(r'^algorithm_delete', views.algorithm_delete),
                       url(r'^algorithm_detail', views.algorithm_detail),
                       url(r'^algorithm', views.algorithm),
                       url(r'^conformer', views.conformer),
                       url(r'^model', views.model),
                       url(r'^m_detail', views.model_detail),
                       url(r'^feature_delete', views.feature_delete),
                       url(r'^feature_detail', views.feature_details),
                       url(r'^features', views.features),
                       url(r'^addfeature', views.add_feature),
                       url(r'^predict_model', views.predict_model),
                       url(r'^predict', views.predict),
                       url(r'^contact', views.contact),
                       url(r'^thanks', views.thanks),
                       url(r'^compound_detail', views.compound_details),
                       url(r'^compound', views.compound),
                       url(r'^source', views.source),
                       url(r'^documentation', views.documentation),
                       url(r'^explore', views.explore),
                       url(r'^stoptask', views.stop_task),
                       # captcha
                       url(r'^captcha/', include('captcha.urls')),



                       # Administration page
                       url(r'^admin/', include(admin.site.urls)),
)
