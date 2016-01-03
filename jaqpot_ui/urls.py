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
                       url(r'^substance', views.all_substance),
                       url(r'^sub', views.sub),
                       url(r'^user', views.user),
                       url(r'^train', views.trainmodel),
                       url(r'^dataset', views.choose_dataset),
                       url(r'^data_detail', views.dataset_detail),
                       url(r'^d_delete', views.dataset_delete),
                       url(r'^predicted_dataset', views.dispay_predicted_dataset),
                       url(r'^data', views.dataset),
                       url(r'^algorithm_delete', views.algorithm_delete),
                       url(r'^algorithm_detail', views.algorithm_detail),
                       url(r'^algorithm', views.algorithm),
                       url(r'^conformer', views.conformer),
                       url(r'^model', views.model),
                       url(r'^m_delete', views.model_delete),
                       url(r'^m_detail', views.model_detail),
                       url(r'^m_pmml', views.model_pmml),
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
                       url(r'^change_params', views.change_params),
                       url(r'^select_substance', views.select_substance),
                       url(r'^get_substance', views.get_substance),
                       url(r'^properties', views.select_properties),
                       url(r'^descriptors', views.select_descriptors),
                       url(r'^calculate_image_descriptors', views.calculate_image_descriptors),
                       url(r'^calculate_mopac_descriptors', views.calculate_mopac_descriptors),
                       url(r'^validate', views.validate),
                       url(r'^valid_params', views.valid_params),
                       url(r'^experimental_params', views.experimental_params),
                       url(r'^experimental', views.experimental),
                       url(r'^d_validate', views.choose_dataset_validate),
                       url(r'^exp_design', views.exp_design),
                       url(r'^interlab_substance', views.interlab_select_substance),


                       # captcha
                       url(r'^captcha/', include('captcha.urls')),
                       #search
                       (r'^search/', include('haystack.urls')),



                       # Administration page
                       #url(r'^admin/$', 'jaqpot_ui.views.task'),
                       url(r'^admin/', include(admin.site.urls)),



)
