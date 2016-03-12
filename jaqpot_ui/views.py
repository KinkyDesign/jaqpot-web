import base64
import os
from urllib import urlencode
#from xlrd.xlsx import ET
import urllib
import urllib2
import urlparse

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from elasticsearch import Elasticsearch
from jaqpot_ui.create_dataset import create_dataset, chech_image_mopac, create_dataset2, create_and_clean_dataset
from jaqpot_ui.get_dataset import paginate_dataset, get_prediction_feature_of_dataset, get_prediction_feature_name_of_dataset
from jaqpot_ui.forms import UserForm, BibtexForm, TrainForm, FeatureForm, ContactForm, SubstanceownerForm, UploadFileForm, TrainingForm, InputForm, NoPmmlForm, SelectPmmlForm, DatasetForm, ValidationForm, ExperimentalParamsForm, ExperimentalForm, UploadForm, \
    InterlabForm
import requests
import json
import datetime
import subprocess
from jaqpot_ui.get_params import get_params, get_params2, get_params3
from settings import EXT_AUTH_URL_LOGIN, EXT_AUTH_URL_LOGOUT, EMAIL_HOST_USER, SERVER_URL
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from jaqpot_ui.templatetags import templates_extras
import jsonpatch
import xmltodict
import elasticsearch
import wget
import collections

# Home page
def index(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

    return render(request, "mainPage.html", {'token': token, 'username': username})


# Authenticate user
def login(request):
    if request.method == 'GET':
        form = UserForm(initial={'username': ''})
        return render(request, "login.html", {'form': form})
    if request.method == 'POST':
        form = UserForm(request.POST)
        if not form.is_valid():
            return render(request, "login.html", {'form': form})
        else:
            username = form['username'].value()
            password = form['password'].value()

            # send request to external authenticator
            r = requests.post(SERVER_URL + '/aa/login', data={'username': username, 'password': password})
            print r.text
            if r.status_code == 200:
                response = json.loads(r.text)
                token = response['authToken']

                # set session request
                request.session['token'] = token
                request.session['username'] = username
                return redirect('/')
            elif r.status_code == 401:
                error = "Wrong username or password"
                return render(request, "login.html", {'form': form, 'error': error})
            else:
                error = "An error occurred. Please try again later."
                return render(request, "login.html", {'form': form, 'error': error})

#User logout
def logout(request):
    token = request.session.get('token', '')
    if token:
        # send request to logout from auth server
        r = requests.post(SERVER_URL + '/aa/logout', headers={'subjectid': token})
        if r.status_code == 200:
            # remove from session
            request.session['token'] = ''
            request.session['username'] = ''

            # send to home page
            return redirect('/')
        else:
            return redirect('/login')
    else:
        return redirect('/')


#List of all tasks
def task(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    #else go to tasks
    all_tasks = []
    #get all tasks with status Running
    headers = {'Accept': 'text/uri-list', 'subjectid': token}
    headers = {'Accept': 'application/json', 'subjectid': token}
    res = requests.get(SERVER_URL+'/task?status=RUNNING&start=0&max=10000', headers=headers)
    list_resp = json.loads(res.text)
    if res.status_code == 200:
        list_run=[]

        for l in list_resp:
            list_run.append({'name': l['_id'], 'status': "running", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "running", 'meta': l['meta']})
        list_run = json.dumps(list_run)
        list_run = json.loads(list_run)

        #get all tasks with status Completed
        res = requests.get(SERVER_URL+'/task?status=COMPLETED&start=0&max=10000', headers=headers)
        list_resp = json.loads(res.text)






        list_complete=[]
        for l in list_resp:
            list_complete.append({'name': l['_id'], 'status': "completed", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "completed", 'meta': l['meta']})
        list_complete= json.dumps(list_complete)
        list_complete = json.loads(list_complete)

        #get all tasks with status Cancelled
        res = requests.get(SERVER_URL+'/task?status=CANCELLED&start=0&max=10000', headers=headers)
        list_resp = json.loads(res.text)

        list_cancelled=[]
        for l in list_resp:

            list_cancelled.append({'name': l['_id'], 'status': "cancelled", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "cancelled", 'meta': l['meta']})
        list_cancelled= json.dumps(list_cancelled)
        list_cancelled = json.loads(list_cancelled)

        #get all tasks with status Error
        res = requests.get(SERVER_URL+'/task?status=ERROR&start=0&max=10000', headers=headers)
        list_resp = json.loads(res.text)

        list_error=[]
        for l in list_resp:

            list_error.append({'name': l['_id'], 'status': "error", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "error", 'meta': l['meta']})
        list_error= json.dumps(list_error)
        list_error = json.loads(list_error)


        #get all tasks with status Queued
        res = requests.get(SERVER_URL+'/task?status=QUEUED&start=0&max=10000', headers=headers)
        list_resp = json.loads(res.text)

        list_queued=[]
        for l in list_resp:

            list_queued.append({'name': l['_id'], 'status': "queued", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "queued", 'meta': l['meta']})
        list_queued= json.dumps(list_queued)
        list_queued = json.loads(list_queued)
        all_tasks= json.dumps(all_tasks)
        all_tasks = json.loads(all_tasks)

        if request.method == 'GET':
            return render(request, "task.html", {'token': token, 'username': username, 'all_tasks': all_tasks ,'list_run': list_run, 'list_complete': list_complete, 'list_cancelled': list_cancelled, 'list_error': list_error, 'list_queued': list_queued})
#More information about each task
def taskdetail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    #status = request.GET.get('status')
    if request.is_ajax():
        output = request.GET.getlist('output')[0]
        name = request.GET.getlist('name')[0]
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/task/'+name, headers=headers)
        data = json.loads(res.text)
        if data['meta']['date']:
            date=data['meta']['date'].split('T')[0]
            data['meta']['date'] = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%y')
        data = json.dumps(data)
        return HttpResponse(data)

    if request.method == 'GET':
        #get task details in rdf format
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/task/'+name, headers=headers)
        #output = json.dumps(res.text)
        output = json.loads(res.text)
        if output['meta']['date']:
            date=output['meta']['date'].split('T')[0]
            output['meta']['date'] = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%y')

        return render(request, "taskdetail.html", {'token': token, 'username': username, 'name': name, 'output': output})

#stop running task
def stop_task(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    id = request.GET.get('id')
    if request.method == 'GET':
        #stop task
        headers = {'content-type': 'text/uri-list', 'subjectid': token}
        res = requests.delete(SERVER_URL+'/task/'+id, headers=headers)
        return render(request, "mainPage.html", {'token': token, 'username': username })

#List of all BibTex
def bibtex(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')

    if request.method == 'GET':
        final_output=[]
        #get all bibtex
        headers = {'Accept': 'application/json', 'subjectid': token}
        headers1 = {'Accept': 'text/uri-list', 'subjectid': token}
        res = requests.get(SERVER_URL+'/bibtex?bibtype=Entry&&&start=0&max=10000', headers=headers1)
        list_resp = res.text
        if res.status_code == 403:
            error = "This request is forbidden (e.g., no authentication token is provided)"
            return render(request, "bibtex.html",
                          {'token': token, 'username': username, 'name': name, 'error': error})
        if res.status_code == 401:
            error = "You are not authorized to access this resource"
            return render(request, "bibtex.html",{'token': token, 'username': username, 'name': name, 'error': error})
        if res.status_code == 500:
            error = "Internal server error - this request cannot be served."
            return render(request, "bibtex.html",{'token': token, 'username': username, 'name': name, 'error': error})
        if res.status_code == 200:
            list_resp = list_resp.splitlines()
            for l in list_resp:
                id = l.split('/bibtex/')[1]
                r = requests.get(l, headers=headers)
                #get json data
                info=json.loads(r.text)
                final_output.append( {"id":id, "info": info })

            return render(request, "bibtex.html", {'token': token, 'username': username, 'name': name, 'final_output': final_output})

#Details of each bibtex
def bib_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    id = request.GET.get('id')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.is_ajax():
        id = request.GET.getlist('id')[0]
        op = request.GET.getlist('op')[0]
        path = request.GET.getlist('path')[0]
        value = request.GET.getlist('value')[0]
        body = json.dumps([{'op': op, 'path': path, 'value': value}])
        #body = jsonpatch.JsonPatch([{'op': op, 'path': path, 'value': value}])
        headers = {"Content-Type":"application/json-patch+json",'subjectid': token }
        #headers = {'Accept': 'application/json-patch+json', 'subjectid': token}
        res = requests.patch(url=SERVER_URL+'/bibtex/'+id, data=body, headers=headers)
        print res.text
        return HttpResponse(res.text)


    if request.method == 'GET':
        #send request
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/bibtex/'+id, headers=headers)
        list_resp = res.text
        #get json data
        details = json.loads(res.text)
        return render(request, "bibdetail.html", {'token': token, 'username': username, 'name': name, 'details': details, 'id':details['_id'],})

#Delete Bibtex
def bib_delete(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    id = request.GET.get('id')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        #delete bibtex
        headers = {'content-type': 'text/uri-list', 'subjectid': token}
        res = requests.delete(SERVER_URL+'/bibtex/'+id, headers=headers)
        return render(request, "mainPage.html", {'token': token, 'username': username })

#Add a Bibtex
def add_bibtex(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        form = BibtexForm(initial={'author': "", 'abstract': "",'title': "",'copyright': "",'address':"", 'year':"", 'pages':"", 'volume':"", 'journal':"", 'keyword':"", 'url':""})

        return render(request, "addbibtex.html", {'token': token, 'username': username, 'name': name, 'form': form})
    if request.method == 'POST':
        form = BibtexForm(request.POST)
        if not form.is_valid():
            error = "Invalid value"
            params = {'form': form, 'error': error, 'token': token, 'username': username, 'name': name}
            return render(request, "addbibtex.html", params)

        json_b= { "bibType":form['type'].value(), 'author': form['author'].value(), 'abstract': form['abstract'].value(), 'title': form['title'].value(),
                 'copyright': form['copyright'].value(),'address':form['address'].value(), 'year': form['year'].value(),
                 'pages':form['pages'].value(), 'volume':form['volume'].value(), 'journal': form['journal'].value(), 'keywords': form['keyword'].value(),
                  'url':form['url'].value()}

        bibtex_entry = json.dumps(json_b)
        bibtex_entry = json.loads(bibtex_entry)
        bibtex_entry = json.dumps(bibtex_entry)

        #send request with the new entry for saving
        headers = {'Content-Type': 'application/json', 'subjectid': token}
        res = requests.post(SERVER_URL+'/bibtex', data = bibtex_entry, headers=headers)
        return render(request, "mainPage.html", {'token': token, 'username': username, 'name': name})

def sub(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')

    if request.method == 'GET':
        return render(request, "bibdetail.html", {'token': token, 'username': username, 'name': name})

#User interface
def user(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')

    if request.method == 'GET':
        headers = {'content-type': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/user/'+ username, headers=headers)
        print res.text
        contacts = json.loads(res.text)
        res1 = requests.get(SERVER_URL+'/user/'+ username+'/quota', headers=headers)
        print res1.text
        percentage = json.loads(res1.text)
        percentage = json.dumps(percentage)
        contacts = json.dumps(contacts)

        return render(request, "user_details.html", {'token': token, 'username': username, 'name': name, 'contacts': contacts, 'percentage': percentage})
#Train model
def trainmodel(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    page = request.GET.get('page')
    last = request.GET.get('last')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        dataset=[]
        headers = {'Accept': 'application/json', 'subjectid': token}
        #get total number of datasets
        res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
        total_datasets= int(res.headers.get('total'))
        if total_datasets%20 == 0:
            last = total_datasets/20
        else:
            last = (total_datasets/20)+1

        if page:
            #page1 is the number of first dataset of page
            page1=int(page) * 20 - 20
            k=str(page1)
            print k
            if page1 <= 1:
                res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
            else:
                res = requests.get(SERVER_URL+'/dataset?start='+k+'&max=20', headers=headers)
        else:
            page = 1
            res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
        data= json.loads(res.text)
        print res.text
        for d in data:
            dataset.append({'name': d['_id'], 'meta': d['meta']})
        print dataset
        proposed=[]
        res1 = requests.get(SERVER_URL+'/dataset/featured?start=0&max=10', headers=headers)
        proposed_data = json.loads(res1.text)
        for p in proposed_data:
            proposed.append({'name': p['_id'], 'meta': p['meta']})
        return render(request, "choose_dataset.html", {'token': token, 'username': username, 'entries2': dataset, 'page': page, 'last':last, 'proposed':proposed})

#choose dataset for training
def choose_dataset(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    form = TrainForm(initial={})
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        dataset = request.GET.get('dataset')
        headers = {'Accept': 'text/uri-list', 'subjectid': token}
        classification_alg = []
        res = requests.get(SERVER_URL+'/algorithm?class=ot:Classification&start=0&max=100', headers=headers)
        list_resp = res.text
        list_resp = list_resp.split('\n')[:]
        for l in list_resp:
            l = l.split('/algorithm/')[1]
            classification_alg.append({'name': l})
        classification_alg = json.dumps(classification_alg)
        classification_alg = json.loads(classification_alg)
        regression_alg = []
        res = requests.get(SERVER_URL+'/algorithm?class=ot:Regression&start=0&max=100', headers=headers)
        list_resp = res.text
        list_resp = list_resp.split('\n')[:]
        for l in list_resp:
            l = l.split('/algorithm/')[1]
            regression_alg.append({'name': l})
        regression_alg = json.dumps(regression_alg)
        regression_alg = json.loads(regression_alg)
        return render(request, "train_model.html", {'token': token, 'username': username, 'classification_alg': classification_alg, 'regression_alg': regression_alg, 'form':form, 'dataset': dataset})
    if request.method == 'POST':
        algorithms=[]
        for alg in request.POST.getlist('radio'):
            headers = {'Accept': 'application/json', 'subjectid': token}
            res = requests.get(SERVER_URL+'/algorithm/'+alg, headers=headers)
            info = json.loads(res.text)
            algorithms.append({"alg":alg, "info":info })
        dataset = request.GET.get('dataset')
        print dataset
        print algorithms
        if algorithms == []:
            headers = {'Accept': 'text/uri-list', 'subjectid': token}
            classification_alg = []
            res = requests.get(SERVER_URL+'/algorithm?class=ot:Classification&start=0&max=100', headers=headers)
            list_resp = res.text
            list_resp = list_resp.split('\n')[:]
            for l in list_resp:
                l = l.split('/algorithm/')[1]
                classification_alg.append({'name': l})
            classification_alg = json.dumps(classification_alg)
            classification_alg = json.loads(classification_alg)
            regression_alg = []
            res = requests.get(SERVER_URL+'/algorithm?class=ot:Regression&start=0&max=100', headers=headers)
            list_resp = res.text
            list_resp = list_resp.split('\n')[:]
            for l in list_resp:
                l = l.split('/algorithm/')[1]
                regression_alg.append({'name': l})
            regression_alg = json.dumps(regression_alg)
            regression_alg = json.loads(regression_alg)
            error = "Please select algorithm."
            return render(request, "train_model.html", {'token': token, 'username': username, 'classification_alg': classification_alg, 'regression_alg': regression_alg, 'form':form, 'dataset': dataset, 'error':error})
        else:
            request.session['alg'] = algorithms[0]['alg']
            request.session['data'] = dataset
            return redirect('/change_params', {'token': token, 'username': username,})
#change algorithms parameters, select pmml, prediction feature, scaling and doa for training
def change_params(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        form = UploadFileForm()
        tform = TrainingForm()
        inputform = InputForm()
        nform = NoPmmlForm()
        pmmlform = SelectPmmlForm()
        dataset = request.session.get('data', '')
        algorithms = request.session.get('alg', '')
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/algorithm/'+algorithms, headers=headers)
        al = json.loads(res.text)
        res1 = requests.get(SERVER_URL+'/pmml/?start=0&max=1000', headers=headers)
        pmml=json.loads(res1.text)
        if pmml:
            pmmlform.fields['pmml'].choices = [(p['_id'],p['_id']) for p in pmml]
        else:
            pmmlform.fields['pmml'].choices = [("",'No pmml')]
        res2 = requests.get(SERVER_URL+'/dataset/'+dataset+'?rowStart=0&rowMax=1&colStart=0&colMax=2', headers={'subjectid':token})
        predicted_features = json.loads(res2.text)
        if str(res2) != "<Response [200]>":
            #redirect to error page
            return render(request, "error.html", {'token': token, 'username': username,'error':predicted_features})
        else:
            features = predicted_features['features']
            form.fields['feature'].choices = [(f['uri'],f['name']) for f in features]
            inputform.fields['input'].choices = [(f['uri'],f['name']) for f in features]
            inputform.fields['output'].choices = [(f['uri'],f['name']) for f in features]
            nform.fields['pred_feature'].choices = [(f['uri'],f['name']) for f in features]
            pmmlform.fields['predicted_feature'].choices = [(f['uri'],f['name']) for f in features]
            return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'al': al, 'algorithms':algorithms, 'uploadform':form, 'tform':tform ,'features':features, 'inputform':inputform, 'nform':nform, 'pmmlform': pmmlform})


    if request.method == 'POST':
        #get parameters of algorithm
        params={}
        print request.POST


        tform = TrainingForm(request.POST)
        inputform = InputForm(request.POST)
        form = UploadFileForm(request.POST, request.FILES)
        nform = NoPmmlForm(request.POST)
        pmmlform = SelectPmmlForm(request.POST)
        dataset = request.session.get('data', '')
        algorithms = request.session.get('alg', '')
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/algorithm/'+algorithms, headers=headers)
        al = json.loads(res.text)
        if request.POST.getlist('parameters'):
            parameters = request.POST.getlist('parameters')
            '''for p in parameters:
                params.append({'name': p, 'value': request.POST.get(''+p)})
                for a in al['parameters']:
                    if (a['name'] == p):
                        print p
                        a['value']=request.POST.get(''+p)'''
            for p in parameters:
                #params.update({p: request.POST.get(''+p)})
                for a in al['parameters']:
                    if (a['name'] == p):
                        print p
                        a['value']=request.POST.get(''+p)
            print al['parameters']
            for a in al['parameters']:
                params.update({a['name']: a['value']})
            params, al = get_params3(request, parameters, al)
            print json.dumps(params)

        res1 = requests.get(SERVER_URL+'/pmml/?start=0&max=1000', headers=headers)
        pmml=json.loads(res1.text)
        if pmml:
            pmmlform.fields['pmml'].choices = [(p['_id'],p['_id']) for p in pmml]
        else:
            pmmlform.fields['pmml'].choices = [("",'No pmml')]
        res2 = requests.get(SERVER_URL+'/dataset/'+dataset+'?rowStart=0&rowMax=1&colStart=0&colMax=2', headers={'subjectid':token})
        predicted_features = json.loads(res2.text)

        if str(res2) != "<Response [200]>":
            #redirect to error page
            return render(request, "error.html", {'token': token, 'username': username,'error':predicted_features})
        else:
            features = predicted_features['features']
            form.fields['feature'].choices = [(f['uri'],f['name']) for f in features]
            inputform.fields['output'].choices = [(f['uri'],f['name']) for f in features]
            inputform.fields['input'].choices = [(f['uri'],f['name']) for f in features]
            nform.fields['pred_feature'].choices = [(f['uri'],f['name']) for f in features]
            pmmlform.fields['predicted_feature'].choices = [(f['uri'],f['name']) for f in features]
        if not tform.is_valid():
            return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'algorithms':algorithms, 'tform':tform, 'uploadform':form,'inputform': inputform, 'al':al, 'nform': nform, 'pmmlform':pmmlform})
        #get transformations
        transformations=""
        prediction_feature = ""
        if request.POST.get('variables') == "none":
            if not nform.is_valid():
                return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'algorithms':algorithms, 'tform':tform, 'uploadform':form,'inputform': inputform, 'al':al, 'nform': nform, 'pmmlform':pmmlform})
            transformations = ""
            prediction_feature = nform['pred_feature'].value()
        elif request.POST.get('variables') == "pm":
            transformations = SERVER_URL+'/pmml/'+pmmlform['pmml'].value()
            prediction_feature = pmmlform['predicted_feature'].value()
        elif request.POST.get('variables') == "input":
            prediction_feature = inputform['output'].value()
            feature_list = inputform['input'].value()
            if not inputform.is_valid():
                return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'algorithms':algorithms, 'tform':tform, 'uploadform':form,'inputform': inputform, 'al':al, 'nform': nform, 'pmmlform':pmmlform})
            headers = {'Accept': 'application/json',  'subjectid': token}
            feat=""
            for f in feature_list:
                feat += str(f)+','
            body = {'features': feat}
            res = requests.post(SERVER_URL+'/pmml/selection', headers=headers, data=body)
            response = json.loads(res.text)
            transformations = SERVER_URL+'/pmml/'+response['_id']

        elif request.POST.get('variables') == "file":
            prediction_feature = form['feature'].value()
            if form.is_valid:
                if 'file' in request.FILES:
                    pmml= request.FILES['file'].read()
                    print pmml
                    headers = {'Content-Type': 'application/xml',  'subjectid': token }
                    res = requests.post(SERVER_URL+'/pmml', headers=headers, data=pmml)
                    print res.text
                    response = json.loads(res.text)
                    transformations = SERVER_URL+'/pmml/'+response['_id']
                else:
                    return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'al': al, 'algorithms':algorithms, 'pmmlform':pmmlform, 'uploadform':form, 'tform':tform, 'features':features, 'inputform': inputform, 'nform': nform})

         #get scaling
        scaling=""
        if request.POST.get('scaling') == "scaling1":
            scaling=""
        elif request.POST.get('scaling') == "scaling2":
            scaling=SERVER_URL+'/algorithm/scaling'
        elif request.POST.get('scaling') == "scaling3":
            scaling=SERVER_URL+'/algorithm/standarization'
        #get doa
        doa=""
        if request.POST.get('doa') == "doa1":
            doa=""
        elif request.POST.get('doa') == "doa2":
            doa=SERVER_URL+'/algorithm/leverage'
        elif request.POST.get('doa') == "doa3":
            doa=SERVER_URL+'/algorithm/leverage'
        algorithms = request.session.get('alg', '')
        dataset = request.session.get('data', '')
        title= tform['modelname'].value()
        description= tform['description'].value()
        body = {'dataset_uri': SERVER_URL+'/dataset/'+dataset, 'scaling': scaling, 'doa': doa, 'title': title, 'description':description, 'transformations':transformations, 'prediction_feature': prediction_feature, 'parameters':json.dumps(params), 'visible': True}
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.post(SERVER_URL+'/algorithm/'+algorithms, headers=headers, data=body)
        print res.text
        task_id = json.loads(res.text)['_id']
        print task_id
        print json.dumps(params)
        return redirect('/t_detail?name='+task_id+'&status=queued', {'token': token, 'username': username})


#Conformer
def conformer(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        return render(request, "conformer.html", {'token': token, 'username': username})
    if request.method == 'POST':
        #add task for descriptors calculation
        return redirect('/task', {'token': token, 'username': username})

#list of models
def model(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        models = []
        #get all models
        headers = {'Accept': 'application/json', "subjectid": token}
        #get total number of models
        res = requests.get(SERVER_URL+'/model?start=0&max=1', headers=headers)
        total_models= res.headers.get('total')
        res = requests.get(SERVER_URL+'/model?start=0&max='+total_models, headers=headers)
        list_resp = json.loads(res.text)
        #for each model
        for l in list_resp:
            models.append({'name': l['_id'], 'meta': l['meta'] })
        models = json.dumps(models)
        models = json.loads(models)
        #Get selected models
        res1 = requests.get(SERVER_URL+'/model/featured?start=0&max=10', headers=headers)
        proposed_model = json.loads(res1.text)
        proposed = []
        for p in proposed_model:
            proposed.append({'name': p['_id'], 'meta': p['meta'] })
        return render(request, "model.html", {'token': token, 'username': username, 'models':models, 'proposed':proposed })

#Display details for each model
def model_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    #get task details in rdf format
    headers = {'Accept': 'application/json', "subjectid": token}
    res = requests.get(SERVER_URL+'/model/'+name, headers=headers)
    details = json.loads(res.text)
    algorithm=details['algorithm']['_id']
    if algorithm:
        res = requests.get(SERVER_URL+'/algorithm/'+algorithm, headers=headers)
        alg_details=json.loads(res.text)
    else:
        alg_details = ""
    res = requests.get(SERVER_URL+'/model/'+name+'/required', headers=headers)
    required= json.loads(res.text)
    required_feature = []
    for r in required:
        required_feature.append({'feature': r['uri']})
    if request.method == 'GET':
        return render(request, "model_detail.html", {'token': token, 'username': username, 'details':details, 'name':name, 'alg': alg_details, 'required':required_feature })

#Delete selected model
def model_delete(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    id = request.GET.get('id')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    #delete model
    headers = {'Accept': 'application/json', "subjectid": token}
    res = requests.delete(SERVER_URL+'/model/'+id, headers=headers)
    reply = res.text
    return redirect('/')


def model_pmml(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    name = request.GET.get('name')
    headers = {'Accept': 'application/xml', "subjectid": token}
    res = requests.get(SERVER_URL+'/model/'+name+'/pmml', headers=headers)
    #details = json.loads(res.text)
    if res.status_code == 200:
        pmml = res.text
        response = HttpResponse(pmml, content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="pmml_'+name+'.xml"'
        return response
    else:
        #response = HttpResponse(res.text,  mimetype="application/json")
        print res.text
        headers = {'Accept': 'application/json', "subjectid": token}
        res1 = requests.get(SERVER_URL+'/model/'+name, headers=headers)
        details = json.loads(res1.text)
        algorithm=details['algorithm']['_id']
        if algorithm:
            res2 = requests.get(SERVER_URL+'/algorithm/'+algorithm, headers=headers)
            alg_details=json.loads(res2.text)
        else:
            alg_details = ""
        res3 = requests.get(SERVER_URL+'/model/'+name+'/required', headers=headers)
        required= json.loads(res3.text)
        required_feature = []
        for r in required:
            required_feature.append({'feature': r['uri']})

        return render(request, "model_detail.html", {'token': token, 'username': username, 'details':details, 'name':name, 'alg': alg_details, 'required':required_feature, 'error': res.text})



#list of features
def features(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    page = request.GET.get('page')
    last = request.GET.get('last')

    if request.method == 'GET':
        headers = {'Accept': 'application/json', 'subjectid': token}
        if page:
            page1=int(page) * 20 - 20
            k=str(page1)
            if page1 <= 1:
                res = requests.get(SERVER_URL+'/feature?start=0&max=20', headers=headers)
            elif last:
                res = requests.get(SERVER_URL+'/feature?start='+last+'&max=20', headers=headers)
            else:
                res = requests.get(SERVER_URL+'/feature?start='+k+'&max=20', headers=headers)

        else:
            page = 1
            res = requests.get(SERVER_URL+'/feature?start=0&max=20', headers=headers)
        features=[]
        if res.status_code == 403:
            error = "This request is forbidden (e.g., no authentication token is provided)"
            return render(request, "features.html", {'token': token, 'username': username, 'error': error})

        if res.status_code == 401:
            error = "You are not authorized to access this resource"
            return render(request, "features.html", {'token': token, 'username': username, 'error': error})

        if res.status_code == 500:
            error = "Internal server error - this request cannot be served."
            return render(request, "features.html", {'token': token, 'username': username, 'error': error})

        if res.status_code == 200:
            #get json feautures
            feature= json.loads(res.text)
            for f in feature:
                features.append({'name': f['_id'], 'meta': f['meta']})
            if len(features)< 20:
                last= page
            return render(request, "features.html", {'token': token, 'username': username, 'features': features, 'page': page, 'last': last})

#Display details of each feature
def feature_details(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    name = request.GET.get('name')

    if request.method == 'GET':
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/feature/'+name, headers=headers)
        feature_detail=json.loads(res.text)
        return render(request, "feature_details.html", {'token': token, 'username': username, 'name': name, 'feature_detail': feature_detail})

#Add feature
def add_feature(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    name = request.GET.get('name')
    if request.method == 'GET':
        form = FeatureForm(initial={'feature': ""})

        return render(request, "add_feature.html", {'token': token, 'username': username, 'name': name, 'form': form})
    if request.method == 'POST':
        form = FeatureForm(request.POST)
        if not form.is_valid():
            error = "Invalid value"
            params = {'form': form, 'error': error, 'token': token, 'username': username, 'name': name}
            return render(request, "add_feature.html", params)

        json_b= {'feature': form['feature'].value() }
        feature_entry = json.dumps(json_b)
        print feature_entry
        #it should send request with the new entry for saving
        return render(request, "mainPage.html", {'token': token, 'username': username, 'name': name})

#Delete feature
def feature_delete(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    id = request.GET.get('id')
    if request.method == 'GET':
        #delete bibtex
        headers = {'content-type': 'text/uri-list', 'subjectid': token}
        res = requests.delete(SERVER_URL+'/feature/'+id, headers=headers)
        return render(request, "mainPage.html", {'token': token, 'username': username })

#List of algorithms
def algorithm(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')

    if request.method == 'GET':
         algorithms = []
         #get all algorithms
         headers = {'Accept': 'text/uri-list', 'subjectid': token}
         res = requests.get(SERVER_URL+'/algorithm?start=0&max=10', headers=headers)
         list_resp = res.text
         list_resp = list_resp.split('\n')[:]
         for l in list_resp:
             l = l.split('/algorithm/')[1]
             algorithms.append({'name': l})
         algorithms = json.dumps(algorithms)
         algorithms = json.loads(algorithms)
         print algorithms

         return render(request, "algorithm.html", {'token': token, 'username': username, 'algorithms': algorithms})

#Display details of each algorithm
def algorithm_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    algorithm = request.GET.get('name')

    if request.method == 'GET':
        #get task details in rdf format
        headers = {'content-type': 'text/uri-list', 'subjectid': token}
        res = requests.get(SERVER_URL+'/algorithm/'+algorithm, headers=headers)
        #get rdf response and convert to json data with details for bibtex
        details = json.loads(res.text)
        return render(request, "algorithm_detail.html", {'token': token, 'username': username, 'details': details, 'id': algorithm})

#Delete algorithm
def algorithm_delete(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    id = request.GET.get('id')
    if request.method == 'GET':
        #delete algorithm
        headers = {'content-type': 'text/uri-list', 'subjectid': token}
        res = requests.delete(SERVER_URL+'/algorithm/'+id, headers=headers)
        return render(request, "mainPage.html", {'token': token, 'username': username})

#List of dataset
def dataset(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')

    page = request.GET.get('page')
    last = request.GET.get('last')
    dataset=[]
    if request.method == 'GET':
        dataset=[]
        headers = {'Accept': 'application/json', 'subjectid': token}
        #get total number of datasets
        res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
        total_datasets= int(res.headers.get('total'))
        if total_datasets%20 == 0:
            last = total_datasets/20
        else:
            last = (total_datasets/20)+1

        if page:
            #page1 is the number of first dataset of page
            page1=int(page) * 20 - 20
            k=str(page1)
            if page1 <= 1:
                res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
            else:
                res = requests.get(SERVER_URL+'/dataset?start='+k+'&max=20', headers=headers)
        else:
            page = 1
            res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
        data= json.loads(res.text)
        for d in data:
            dataset.append({'name': d['_id'], 'meta': d['meta']})
        res1 = requests.get(SERVER_URL+'/dataset/featured?start=0&max=10', headers=headers)
        proposed_data = json.loads(res1.text)
        proposed = []
        for p in proposed_data:
            proposed.append({'name': p['_id'], 'meta': p['meta'] })
        return render(request, "dataset.html", {'token': token, 'username': username, 'dataset': dataset, 'page': page, 'last':last, 'proposed':proposed})

#Display details of each dataset
def dataset_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')

    name = request.GET.get('name', '')
    page = request.GET.get('page', '')
    data_detail, last, page = paginate_dataset(request, name, token, username, page)
    if data_detail and last and page:
            a=[]
            #a=collections.OrderedDict()
            # a contains all compound's properties
            for key in data_detail['dataEntry']:
                for k, value in key.items():
                    if k =='values':
                        counter=0
                        for m,n in value.items():
                            if m not in a:
                                a.append(m)
                                '''a[counter]=m
                                counter=counter+1'''

            print a
            properties={}
            new=[]
            compound = []
            for i in range(len(a)):
                for k in data_detail['features']:
                    if k['uri'] == a[i]:
                        new.append(k)

            #get response json
            for key in data_detail['dataEntry']:
                properties[key['compound']['URI']] = []
                properties[key['compound']['URI']].append({"compound": key['compound']['URI']})
                properties[key['compound']['URI']].append({"name": key['compound']['name']})

                #for each compound
                for k, value in key.items():
                    if k =='values':
                        for i in range(len(a)):
                            #if a compound haven't value for a property add its value Null
                            if a[i] in value:
                                properties[key['compound']['URI']].append({"prop": a[i], "value": value[a[i]]})
                            else:
                                properties[key['compound']['URI']].append({"prop":  a[i], "value": "NULL"})

            return render(request, "dataset_detail.html", {'token': token, 'username': username, 'name': name, 'data_detail':data_detail, 'properties': properties, 'a': a, 'new': new, 'page':page, 'last':last})

#Delete selected dataset
def dataset_delete(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    id = request.GET.get('id')
    #delete dataset
    headers = {'Accept': 'application/json', "subjectid": token}
    res = requests.delete(SERVER_URL+'/dataset/'+id, headers=headers)
    reply = res.text
    print reply
    return redirect('/data')

def dispay_predicted_dataset(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    name = request.GET.get('name', '')
    page = request.GET.get('page', '')
    model = request.GET.get('model', '')
    data_detail, last, page = paginate_dataset(request, name, token, username, page)
    if data_detail and last and page:
        headers = {'Accept': 'text/uri-list', "subjectid": token}
        res = requests.get(SERVER_URL+'/model/'+model+'/predicted', headers=headers)
        predicted =  res.text
        predicted = predicted.splitlines()
        properties={}
        new=[]
        for i in range(len(predicted)):
            for k in data_detail['features']:
                if k['uri'] == predicted[i]:
                    new.append(k['name'])
        res = requests.get(SERVER_URL+'/model/'+model+'/dependent', headers=headers)
        dependent =  res.text
        if dependent:
            dependent = dependent.splitlines()
            for i in range(len(dependent)):
                for k in data_detail['features']:
                    if k['uri'] == dependent[i]:
                        new.append(k['name'])
        #get response json
        for key in data_detail['dataEntry']:
            properties[key['compound']['URI']] = []
            properties[key['compound']['URI']].append({"compound": key['compound']['URI']})
            properties[key['compound']['URI']].append({"name": key['compound']['name']})
            for p in predicted:
                properties[key['compound']['URI']].append({"prop": p, "value": key['values'][p]})

        return render(request, "predicted_dataset.html", {'token': token, 'username': username, 'name': name,'data_detail':data_detail, 'properties': properties, 'new': new, 'a':predicted, 'page':page, 'last':last, 'model':model })

#Predict model
def predict(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

    #Check if user is authenticated. Else redirect to login page
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        m = []
        #get all models
        headers = {'Accept': 'application/json', "subjectid": token}
        res = requests.get(SERVER_URL+'/model?start=0&max=10000', headers=headers)
        list_resp = res.text
        models = json.loads(res.text)
        print models
        for mod in models:
                m.append({'name': mod['_id'], 'meta': mod['meta']})
        #Get selected models
        res1 = requests.get(SERVER_URL+'/model/featured?start=0&max=10', headers=headers)
        proposed_model = json.loads(res1.text)
        proposed = []
        for p in proposed_model:
            proposed.append({'name': p['_id'], 'meta': p['meta'] })
        #Display all models for selection
        return render(request, "predict_model.html", {'token': token, 'username': username, 'my_models': m, 'proposed':proposed})


def predict_model(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    #Get the current page
    page = request.GET.get('page')
    #Get the last page
    last = request.GET.get('last')
    if request.method == 'GET':
        #Get the selected model for prediction
        model = request.GET.get('model')
        #Save selected model at session model
        request.session['model'] = model
        dataset=[]
        #Get required feature of selected model
        headers = {'Accept': 'application/json', 'subjectid': token}
        required_res = requests.get(SERVER_URL+'/model/'+model+'/required', headers=headers)
        model_req = json.loads(required_res.text)
        #check if is needed image or mocap
        image, mopac = chech_image_mopac(model_req)
        #Firstly, get the datasets of first page if user selects different page get the datasets of the selected page
        if page:
            page1=int(page) * 20 - 20
            k=str(page1)
            if page1 <= 1:
                res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
            elif last:
                res = requests.get(SERVER_URL+'/dataset?start='+last+'&max=20', headers=headers)
            else:
                res = requests.get(SERVER_URL+'/dataset?start='+k+'&max=20', headers=headers)

        else:
            page = 1
            res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
        data= json.loads(res.text)
        for d in data:
            dataset.append({'name': d['_id'], 'title':d['meta']['titles'][0], 'description': d['meta']['descriptions'][0]})

        if len(dataset)< 20:
            last= page
        res1 = requests.get(SERVER_URL+'/dataset/featured?start=0&max=10', headers=headers)
        proposed_data = json.loads(res1.text)
        proposed = []
        for p in proposed_data:
            proposed.append({'name': p['_id'], 'meta': p['meta'] })
        #Display all datasets for selection
        return render(request, "predict.html", {'token': token, 'username': username, 'dataset': dataset, 'page': page, 'last':last, 'model_req': model_req, 'model' : model, 'image':image, 'mopac':mopac, 'proposed':proposed})
    if request.method == 'POST':
        #Get the selected model for prediction from session
        selected_model= request.session.get('model', '')
        #Get the method of prediction
        method = request.POST.get('radio_method')
        #Get the required model
        headers = {'Accept': 'application/json', 'subjectid': token}
        required_res = requests.get(SERVER_URL+'/model/'+selected_model+'/required', headers=headers)
        required_res = json.loads(required_res.text)
        print required_res
        if request.is_ajax():
            img_descriptors = request.POST.getlist('img_desc[]')
            mopac_descriptors = request.POST.getlist('mopac_desc[]')
            print mopac_descriptors
            print request.POST
            if 'excel_data' in request.POST:
                data = request.POST.get('excel_data')
                data = json.loads(data)
                n_data=[]
                n_d={}
                n_d1={}
                for d in data:
                    for key, value in d.items():
                        new_val = value.replace(',', '.')
                        n_d1[''+key+'']=new_val
                        n_d.update(n_d1)
                n_data.append(n_d)
                print n_data
                data = n_data
                #data = json.loads(data)
                #data.replace(',','.')'''
                print data
                #Get data from excel and create dataset to the appropriate format
                new_data = create_dataset(data,username,required_res, img_descriptors, mopac_descriptors)
                json_data = json.dumps(new_data)
                print json_data
                headers1 = {'Content-type': 'application/json', 'subjectid': token}
                res = requests.post(SERVER_URL+'/dataset', headers=headers1, data=json_data)
                dataset =  res.text
                print dataset
                headers = {'Accept': 'application/json', "subjectid": token}
                body = {'dataset_uri': dataset, 'visible': True}
                print selected_model
                res = requests.post(SERVER_URL+'/model/'+selected_model, headers=headers, data=body)
                response = json.loads(res.text)
                print response
                id = response['_id']

            return HttpResponse(id)
        if method == 'select_dataset':
            #Get the selected dataset
            dataset = request.POST.get('radio')
            print request.POST
            if dataset == "" or dataset == None:
                m = []
                #get all models
                headers = {'Accept': 'application/json', "subjectid": token}
                res = requests.get(SERVER_URL+'/model?start=0&max=10000', headers=headers)
                models = json.loads(res.text)
                for mod in models:
                        m.append({'name': mod['_id'], 'meta': mod['meta']})
                return render(request, "predict.html", {'token': token, 'username': username,'selected_model': selected_model, 'page': page, 'last':last,'error':"You should select a dataset."})
            else:
                headers = {'Accept': 'application/json', "subjectid": token}
                body = {'dataset_uri': SERVER_URL+'/dataset/'+dataset, 'visible': True}
                res = requests.post(SERVER_URL+'/model/'+selected_model, headers=headers, data=body)
                response = json.loads(res.text)
                print response
                id = response['_id']
                return redirect('/t_detail?name='+id+'&model='+selected_model)

def calculate_image_descriptors(request):
    #get data uri od upload image
    data_uri = request.GET.get('data_uri')
    print data_uri
    #send request to data uri
    body = {'image': data_uri, }
    res = requests.post('http://test.jaqpot.org:8880/imageAnalysis/service/analyze', data=body)
    response = json.loads(res.text)
    for r in response:
        if r['id'] == "Average Particle":
            average_particle = r
    print average_particle
    return HttpResponse(json.dumps(average_particle))

def calculate_mopac_descriptors(request):
    token = request.session.get('token', '')
    #Check if user is authenticated. Else redirect to login page
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    headers = {'subjectid': token}
    mopac_file = request.GET.get('mopac_file')
    body = {'pdbfile': mopac_file ,}
    res = requests.post('http://test.jaqpot.org:8080/algorithms/service/mopac/calculate', headers=headers, data=body)
    print res.text
    response = json.loads(res.text)
    print response
    return HttpResponse(json.dumps(response))
#Search
def search(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        search = request.GET.get('search')
        models=[]
        headers = {'Accept': 'text/uri-list', "subjectid": token}
        res = requests.get(SERVER_URL+'/model?start=0&max=10000', headers=headers)
        list_resp = res.text
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        #get each line
        list_resp = list_resp.splitlines()
        i=1
        for l in list_resp:
            l = l.split('/model/')[1]
            models.append({'name': l})
            es.index(index='name', doc_type='models', id=i, body={'name': l})
            i=i+1
        models = json.dumps(models)
        models = json.loads(models)
        print es.get(index='name', doc_type='models', id=2)
        return HttpResponse(models)
#Contact form
def contact(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')

    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']

            recipients = [ EMAIL_HOST_USER ]
            #css the sender mail
            recipients.append(sender)
            send_mail(subject, message, sender, recipients)
            return HttpResponseRedirect('/thanks/') # Redirect after POST
        else:

            return render_to_response('contact_form.html', {'form': form, 'token': token, 'username': username}, context_instance=RequestContext(request))
    else:
        form = ContactForm() # An unbound form

    return render_to_response('contact_form.html', {'form': form, 'token': token, 'username': username}, context_instance=RequestContext(request))

#redirect to thanks page
def thanks(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        return render(request, "thanks.html", {'token': token, 'username': username})

def compound(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        compound= [{'name':'compound1'}, {'name':'compound2'}, {'name':'compound3'}, {'name':'compound4'}]
        return render(request, "compound.html", {'token': token, 'username': username, 'compound': compound})

def compound_details(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    name = request.GET.get('name', '')
    if request.method == 'GET':
        return render(request, "compound_detail.html", {'token': token, 'username': username, 'name': name})

#redirect to source page
def source(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        return render(request, "source.html", {'token': token, 'username': username})

#redirect to documentation page
def documentation(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        return render(request, "documentation.html", {'token': token, 'username': username})

def explore(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    entries = [ "data", "data2", "data3"]
    entries2 = [ "compound", "compound2", "compound3"]
    entries3 = [ "conformer", "conformer2", "conformer3"]
    if request.method == 'GET':
        return render(request, "explore.html", {'token': token, 'username': username, 'entries': entries, 'entries_2':entries2, 'entries_3':entries3})
#Create dataset
def all_substance(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
        else:
            page=request.GET.get('page')
            if page:
                headers = {'Accept': 'application/json', 'subjectid': token}
                page1=str(int(page)-1)
                res = requests.get('https://apps.ideaconsult.net:443/enmtest/substanceowner?page='+page1+'&pagesize=20', headers=headers)
                substance_owner=json.loads(res.text)
                substance_owner = substance_owner['facet']
            else:
                headers = {'Accept': 'application/json', 'subjectid': token}
                page=1
                res = requests.get('https://apps.ideaconsult.net:443/enmtest/substanceowner?page=0&pagesize=20', headers=headers)
                substance_owner=json.loads(res.text)
                substance_owner = substance_owner['facet']
    else:
        return redirect('/login')
    if request.method == 'GET':
        form = SubstanceownerForm(initial={'substanceowner': ''})
        if len(substance_owner)<20:
            last=page
            return render(request, "substance.html", {'token': token, 'username': username, 'form':form, 'substance_owner': substance_owner, 'page': page, 'last':last,})
        else:
            return render(request, "substance.html", {'token': token, 'username': username, 'form':form, 'substance_owner': substance_owner, 'page': page})
    if request.method == 'POST':
        method = request.POST.get('radio_method')
        if method=="select":
            substance_owner = request.POST.get('radio')
            if not substance_owner:
                form = SubstanceownerForm(initial={'substanceowner': ''})
                page=request.GET.get('page')
                if page:
                    headers = {'Accept': 'application/json', 'subjectid': token}
                    page1=str(int(page)-1)
                    res = requests.get('https://apps.ideaconsult.net:443/enmtest/substanceowner?page='+page1+'&pagesize=20', headers=headers)
                    substance_owner=json.loads(res.text)
                    substance_owner = substance_owner['facet']
                else:
                    headers = {'Accept': 'application/json', 'subjectid': token}
                    page=1
                    res = requests.get('https://apps.ideaconsult.net:443/enmtest/substanceowner?page=0&pagesize=20', headers=headers)
                    substance_owner=json.loads(res.text)
                    substance_owner = substance_owner['facet']
                error = "Please select substance owner."
                return render(request, "substance.html", {'token': token, 'username': username, 'form':form, 'substance_owner': substance_owner, 'page': page, 'error':error})
            else:
                substance_owner = 'https://apps.ideaconsult.net/enmtest/substanceowner/'+substance_owner
                request.session['substanceowner']= substance_owner
                headers = {'Accept': 'application/json', 'subjectid': token}
                res = requests.get(substance_owner+'/substance', headers=headers)
                substances=json.loads(res.text)
                request.session['substances'] = substances
                return redirect('/select_substance', {'token': token, 'username': username})
        elif method=="complete":
            form = SubstanceownerForm(request.POST)
            if form.is_valid(): # All validation rules pass
                substanceowner = form.cleaned_data['substanceowner']
                print substanceowner
                request.session['substanceowner']=substanceowner
                headers = {'Accept': 'application/json', 'subjectid': token}
                res = requests.get(substanceowner+'/substance', headers=headers)
                substances=json.loads(res.text)
                print substances
                request.session['substances'] = substances
                return redirect('/select_substance', {'token': token, 'username': username})
            else:
                error = "Fill in Substance owner id."
                return render(request, "substance.html", {'token': token, 'username': username, 'form':form, 'error':error,'substance_owner': substance_owner, 'page': page})

def select_substance(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.is_ajax():
            checkall = request.GET.get('checkall')
            print checkall
            print('is ajax')
            substances = request.session.get('substances', '')
            sel = substances['substance']
            checkall=[]
            for s in sel:
                checkall.append(s['URI'])
            print checkall
            checkall=json.dumps(checkall)
            #return redirect('/select_substance', {'token': token, 'username': username, 'checkall':checkall})
            return HttpResponse(checkall)
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
        if request.method == 'GET':
            substances = request.session.get('substances', '')
            print substances
            return render(request, "select_substance.html", {'token': token, 'username': username, 'substances':substances['substance']})
    else:
        return redirect('/login')

def get_substance(request):
     token = request.session.get('token', '')
     username = request.session.get('username', '')
     if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
     else:
        return redirect('/login')
     if request.method == 'GET':
            data= request.GET.getlist('data[]')
            request.session['selected_substances'] = data
            headers = {'Accept': 'application/json', 'subjectid': token}
            res1 = requests.get(SERVER_URL+'/enm/property/categories', headers=headers)
            properties=json.loads(res1.text)
            request.session['properties'] = properties
            print data
            return HttpResponse(data)

def select_properties(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
        if request.method == 'GET':
            properties = request.session.get('properties', '')
            return render(request, "properties.html", {'token': token, 'username': username, 'properties':properties})
        if request.method == 'POST':
            sub= request.POST.getlist('checkbox')
            final={}
            pr=[]
            if "P-CHEM" in sub:
                pr.append("P-CHEM")
            if "ENV FATE" in sub:
                pr.append("ENV FATE")
            if "TOX" in sub:
                pr.append("TOX")
            if "ECOTOX" in sub:
                pr.append("ECOTOX")
            i=0
            j=1
            for p in pr:
                sunbst=[]
                if j<len(pr):
                    while sub[i] != pr[j]:
                        sunbst.append(sub[i])
                        i=i+1
                    final.update({p : sunbst[1:]})
                else:
                     while i<len(sub):
                         sunbst.append(sub[i])
                         i=i+1
                     final.update({p : sunbst[1:]})
                j=j+1
            print final
            request.session['selected_properties'] = final
            return redirect('/descriptors', {'token': token, 'username': username})
    else:
        return redirect('/login')

def select_descriptors(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
        if request.method == 'GET':
            form=DatasetForm()
            headers = {'Accept': 'application/json', 'subjectid': token}
            res1 = requests.get(SERVER_URL+'/enm/descriptor/categories', headers=headers)
            descriptors=json.loads(res1.text)
            print descriptors
            return render(request, "descriptors.html", {'token': token, 'username': username, 'descriptors':descriptors, 'form':form})
        if request.method == 'POST':
            form = DatasetForm(request.POST)
            if not form.is_valid():
                headers = {'Accept': 'application/json', 'subjectid': token}
                res1 = requests.get(SERVER_URL+'/enm/descriptor/categories', headers=headers)
                descriptors=json.loads(res1.text)
                return render(request, "descriptors.html", {'token': token, 'username': username, 'descriptors':descriptors, 'form':form})
            title = form['title'].value()
            description = form['description'].value()
            select_descriptors = request.POST.getlist('checkbox')
            substanceowner = request.session.get('substanceowner', '')
            selected_substances = request.session.get('selected_substances', '')
            selected_properties = request.session.get('selected_properties', '')
            headers = {'content-type': 'application/json', 'subjectid': token}
            body = json.dumps({'description': 'a bundle with protein corona data', 'substanceOwner': substanceowner, 'substances': selected_substances, 'properties': selected_properties})
            res = requests.post(url=SERVER_URL+'/enm/bundle', data=body, headers=headers)
            headers = {'content-type': 'application/json', 'subjectid': token,}
            body = json.dumps({'bundle':res.text, 'descriptors':select_descriptors, 'title': title, 'description':description})
            res = requests.post(url=SERVER_URL+'/enm/dataset', headers=headers, data=body)
            response = json.loads(res.text)
            task = response['_id']
            #return redirect('/task', {'token': token, 'username': username})
            return render(request, "new_task.html", {'token': token, 'username': username, 'task':task})
    else:
        return redirect('/login')

#Validate

def validate(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    page = request.GET.get('page')
    last = request.GET.get('last')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        dataset=[]
        headers = {'Accept': 'application/json', 'subjectid': token}
        #get total number of datasets
        res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
        total_datasets= int(res.headers.get('total'))
        if total_datasets%20 == 0:
            last = total_datasets/20
        else:
            last = (total_datasets/20)+1

        if page:
            #page1 is the number of first dataset of page
            page1=int(page) * 20 - 20
            k=str(page1)
            print k
            if page1 <= 1:
                res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
            else:
                res = requests.get(SERVER_URL+'/dataset?start='+k+'&max=20', headers=headers)
        else:
            page = 1
            res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
        data= json.loads(res.text)
        print res.text
        for d in data:
            dataset.append({'name': d['_id'], 'meta': d['meta']})
        print dataset
        res1 = requests.get(SERVER_URL+'/dataset/featured?start=0&max=10', headers=headers)
        proposed_data = json.loads(res1.text)
        proposed = []
        for p in proposed_data:
            proposed.append({'name': p['_id'], 'meta': p['meta'] })
        return render(request, "choose_dataset_validate.html", {'token': token, 'username': username, 'entries2': dataset, 'page': page, 'last':last, 'proposed': proposed})

#choose dataset for validation
def choose_dataset_validate(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    form = TrainForm(initial={})
    if request.method == 'GET':
        dataset = request.GET.get('dataset')
        headers = {'Accept': 'text/uri-list', 'subjectid': token}
        classification_alg = []
        res = requests.get(SERVER_URL+'/algorithm?class=ot:Classification&start=0&max=100', headers=headers)
        list_resp = res.text
        list_resp = list_resp.split('\n')[:]
        for l in list_resp:
            l = l.split('/algorithm/')[1]
            classification_alg.append({'name': l})
        classification_alg = json.dumps(classification_alg)
        classification_alg = json.loads(classification_alg)
        regression_alg = []
        res = requests.get(SERVER_URL+'/algorithm?class=ot:Regression&start=0&max=100', headers=headers)
        list_resp = res.text
        list_resp = list_resp.split('\n')[:]
        for l in list_resp:
            l = l.split('/algorithm/')[1]
            regression_alg.append({'name': l})
        regression_alg = json.dumps(regression_alg)
        regression_alg = json.loads(regression_alg)
        return render(request, "train_model.html", {'token': token, 'username': username, 'classification_alg': classification_alg, 'regression_alg': regression_alg, 'form':form, 'dataset': dataset, 'validate': True})
    if request.method == 'POST':
        algorithms=[]
        for alg in request.POST.getlist('radio'):
            headers = {'Accept': 'application/json', 'subjectid': token}
            res = requests.get(SERVER_URL+'/algorithm/'+alg, headers=headers)
            info = json.loads(res.text)
            algorithms.append({"alg":alg, "info":info })
        dataset = request.GET.get('dataset')
        print dataset
        print algorithms
        if algorithms == []:
            headers = {'Accept': 'text/uri-list', 'subjectid': token}
            classification_alg = []
            res = requests.get(SERVER_URL+'/algorithm?class=ot:Classification&start=0&max=100', headers=headers)
            list_resp = res.text
            list_resp = list_resp.split('\n')[:]
            for l in list_resp:
                l = l.split('/algorithm/')[1]
                classification_alg.append({'name': l})
            classification_alg = json.dumps(classification_alg)
            classification_alg = json.loads(classification_alg)
            regression_alg = []
            res = requests.get(SERVER_URL+'/algorithm?class=ot:Regression&start=0&max=100', headers=headers)
            list_resp = res.text
            list_resp = list_resp.split('\n')[:]
            for l in list_resp:
                l = l.split('/algorithm/')[1]
                regression_alg.append({'name': l})
            regression_alg = json.dumps(regression_alg)
            regression_alg = json.loads(regression_alg)
            error = "Please select algorithm."
            return render(request, "train_model.html", {'token': token, 'username': username, 'classification_alg': classification_alg, 'regression_alg': regression_alg, 'form':form, 'dataset': dataset, 'error':error, 'validate':True})
        else:
            request.session['alg'] = algorithms[0]['alg']
            request.session['data'] = dataset
            return redirect('/valid_params', {'token': token, 'username': username,})

def valid_params(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        dataset = request.session.get('data', '')
        algorithms = request.session.get('alg', '')
        vform = ValidationForm()
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/algorithm/'+algorithms, headers=headers)
        al = json.loads(res.text)
        res2 = requests.get(SERVER_URL+'/dataset/'+dataset+'?rowStart=0&rowMax=1&colStart=0&colMax=2',headers={'subjectid': token})
        predicted_features = json.loads(res2.text)
        if str(res2) != "<Response [200]>":
            #redirect to error page
            return render(request, "error.html", {'token': token, 'username': username,'error':predicted_features})
        else:
            features = predicted_features['features']
            vform.fields['pred_feature'].choices = [(f['uri'],f['name']) for f in features]

        return render(request, "validate.html", {'token': token, 'username': username, 'dataset':dataset, 'al': al, 'algorithms':algorithms,'features':features, 'vform':vform})
    if request.method == 'POST':
        print("post")
        #get parameters of algorithm
        params=[]
        print request.POST
        parameters = request.POST.getlist('parameters')
        for p in parameters:
            params.append({'name': p, 'value': request.POST.get(''+p)})
        vform = ValidationForm(request.POST)
        dataset = request.session.get('data', '')
        algorithms = request.session.get('alg', '')
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/algorithm/'+algorithms, headers=headers)
        al = json.loads(res.text)
        params, al = get_params3(request, parameters, al)
        #replace al parameters value with request.post
        #al['parameters']= params
        print json.dumps(params)
        res2 = requests.get(SERVER_URL+'/dataset/'+dataset+'?rowStart=0&rowMax=1&colStart=0&colMax=2', headers={'subjectid': token})
        predicted_features = json.loads(res2.text)
        if str(res2) != "<Response [200]>":
            #redirect to error page
            return render(request, "error.html", {'token': token, 'username': username,'error':predicted_features})
        else:
            features = predicted_features['features']
            vform.fields['pred_feature'].choices = [(f['uri'],f['name']) for f in features]
        if not vform.is_valid():
            print vform
            return render(request, "validate.html", {'token': token, 'username': username, 'dataset':dataset, 'algorithms':algorithms, 'vform':vform,'al':al,})

        prediction_feature =  vform['pred_feature'].value()
        folds = vform['folds'].value()
        stratify = vform['stratify'].value()
        '''if stratify != "":
            seed = "5"
        else:
            seed = "" '''
        print prediction_feature
        print params

        body = {'training_dataset_uri': SERVER_URL+'/dataset/'+dataset, 'prediction_feature': prediction_feature, 'algorithm_params':json.dumps(params), 'algorithm_uri': SERVER_URL+'/algorithm/'+algorithms, 'folds':folds, 'stratify': stratify,}

        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.post(SERVER_URL+'/validation/training_test_cross', headers=headers, data=body)
        print res.text
        task_id = json.loads(res.text)['_id']
        print task_id
        return redirect('/t_detail?name='+task_id+'&status=queued', {'token': token, 'username': username})

#Display report after validation
def report(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        name = request.GET.get('name')
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/report/'+name, headers=headers)
        report = json.loads(res.text)
        return render(request, "report.html", {'token': token, 'username': username, 'report': report, 'name':name })


#Experimental design
def experimental(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    page = request.GET.get('page')
    last = request.GET.get('last')
    last = 1
    page=1

    if request.method == 'GET':
        dataset=[]
        headers = {'Accept': 'application/json', 'subjectid': token}
        #get total number of datasets
        '''res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
        total_datasets= int(res.headers.get('total'))
        if total_datasets%20 == 0:
            last = total_datasets/20
        else:
            last = (total_datasets/20)+1

        if page:
            #page1 is the number of first dataset of page
            page1=int(page) * 20 - 20
            k=str(page1)
            if page1 <= 1:
                res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
            else:
                res = requests.get(SERVER_URL+'/dataset?start='+k+'&max=20', headers=headers)
        else:
            page = 1
            res = requests.get(SERVER_URL+'/dataset?start=0&max=20', headers=headers)
        data= json.loads(res.text)'''
        res = requests.get(SERVER_URL+'/dataset/ayDPMNB3JcOJAm', headers=headers)
        data= json.loads(res.text)
        dataset.append({'name': data['_id'], 'meta': data['meta']})
        res1 = requests.get(SERVER_URL+'/dataset/featured?start=0&max=10', headers=headers)
        proposed_data = json.loads(res1.text)
        proposed = []
        for p in proposed_data:
            proposed.append({'name': p['_id'], 'meta': p['meta'] })
        return render(request, "exp_dataset.html", {'token': token, 'username': username, 'dataset': dataset, 'page': page, 'last':last, 'proposed':proposed})

#Select parameters for experimental design with input
def experimental_params(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        dataset = request.GET.get('dataset')
        request.session['alg'] = "ocpu-expdesign-xy"
        request.session['data'] = dataset
        prediction_feature = get_prediction_feature_of_dataset(dataset, token)
        form = UploadForm()
        tform = ExperimentalForm()
        inputform = InputForm()
        #nform = NoPmmlForm()
        pmmlform = SelectPmmlForm()
        headers = {'Accept': 'application/json', 'subjectid': token}
        print prediction_feature
        if prediction_feature == "":
            request.session['alg'] = "ocpu-expdesign-x"
            res = requests.get(SERVER_URL+'/algorithm/ocpu-expdesign-x', headers=headers)
        else:
            res = requests.get(SERVER_URL+'/algorithm/ocpu-expdesign-xy', headers=headers)
        al = json.loads(res.text)
        res1 = requests.get(SERVER_URL+'/pmml/?start=0&max=1000', headers=headers)
        pmml=json.loads(res1.text)
        if pmml:
            pmmlform.fields['pmml'].choices = [(p['_id'],p['_id']) for p in pmml]
        else:
            pmmlform.fields['pmml'].choices = [("",'No pmml')]
        res2 = requests.get(SERVER_URL+'/dataset/'+dataset+'?rowStart=0&rowMax=1&colStart=0&colMax=2', headers={'subjectid': token})
        predicted_features = json.loads(res2.text)
        if str(res2) != "<Response [200]>":
            #redirect to error page
            return render(request, "error.html", {'token': token, 'username': username,'error':predicted_features})
        else:
            features = predicted_features['features']
            form.fields['feature'] = prediction_feature
            inputform.fields['input'].choices = [(f['uri'],f['name']) for f in features]
            if prediction_feature == "":
                inputform.fields['output'].choices = [ (prediction_feature, "")]
            else:
                 inputform.fields['output'].choices = [ (prediction_feature, get_prediction_feature_name_of_dataset(dataset, token, prediction_feature) )]
            pmmlform.fields['predicted_feature'] = prediction_feature

            return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'al': al, 'uploadform':form, 'tform':tform ,'features':features, 'inputform':inputform, 'pmmlform': pmmlform, 'exp':True})

    if request.method == 'POST':
            #get parameters of algorithm
            params=[]
            print request.POST

            tform = ExperimentalForm(request.POST)
            inputform = InputForm(request.POST)
            form = UploadForm(request.POST, request.FILES)
            #nform = NoPmmlForm(request.POST)
            pmmlform = SelectPmmlForm(request.POST)
            dataset = request.session.get('data', '')
            prediction_feature = get_prediction_feature_of_dataset(dataset, token)
            algorithms = request.session.get('alg', '')
            print algorithms
            headers = {'Accept': 'application/json', 'subjectid': token}
            res = requests.get(SERVER_URL+'/algorithm/'+algorithms, headers=headers)
            al = json.loads(res.text)
            parameters = request.POST.getlist('parameters')
            params, al = get_params(request, parameters, al)

            '''for p in parameters:
                params.append({'name': p, 'value': request.POST.get(''+p)})
                for a in al['parameters']:
                    if (a['name'] == p):
                        print p
                        a['value']=request.POST.get(''+p)'''
            print al['parameters']
            res1 = requests.get(SERVER_URL+'/pmml/?start=0&max=1000', headers=headers)
            pmml=json.loads(res1.text)
            if pmml:
                pmmlform.fields['pmml'].choices = [(p['_id'],p['_id']) for p in pmml]
            else:
                pmmlform.fields['pmml'].choices = [("",'No pmml')]
            res2 = requests.get(SERVER_URL+'/dataset/'+dataset+'?rowStart=0&rowMax=1&colStart=0&colMax=2', headers={'subjectid': token})
            predicted_features = json.loads(res2.text)
            if str(res2) != "<Response [200]>":
                #redirect to error page
                return render(request, "error.html", {'token': token, 'username': username,'error':predicted_features})
            else:
                features = predicted_features['features']
                #form.fields['feature'] = prediction_feature
                inputform.fields['input'].choices = [(f['uri'],f['name']) for f in features]
                if prediction_feature== "":
                    inputform.fields['output'].choices = [ (prediction_feature, "")]
                else:
                    inputform.fields['output'].choices = [ (prediction_feature, get_prediction_feature_name_of_dataset(dataset, token, prediction_feature))]
                pmmlform.fields['predicted_feature'] = prediction_feature
            if not tform.is_valid():
                return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'algorithms':algorithms, 'tform':tform, 'uploadform':form,'inputform': inputform, 'al':al, 'pmmlform':pmmlform, 'exp':True})
            #get transformations
            transformations=""
            if request.POST.get('variables') == "none":
                transformations = ""
                prediction_feature = prediction_feature
            elif request.POST.get('variables') == "pm":
                transformations = SERVER_URL+'/pmml/'+pmmlform['pmml'].value()
                prediction_feature = prediction_feature
            elif request.POST.get('variables') == "input":
                prediction_feature = prediction_feature
                feature_list = inputform['input'].value()
                if not inputform.is_valid():
                    return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'algorithms':algorithms, 'tform':tform, 'uploadform':form,'inputform': inputform, 'al':al, 'pmmlform':pmmlform, 'exp':True})
                headers = {'Accept': 'application/json',  'subjectid': token}
                feat=""
                for f in feature_list:
                    feat += str(f)+','
                body = {'features': feat}
                res = requests.post(SERVER_URL+'/pmml/selection', headers=headers, data=body)
                response = json.loads(res.text)
                transformations = SERVER_URL+'/pmml/'+response['_id']

            elif request.POST.get('variables') == "file":
                prediction_feature = prediction_feature
                if form.is_valid:
                    if 'file' in request.FILES:
                        pmml= request.FILES['file'].read()
                        print pmml
                        headers = {'Content-Type': 'application/xml',  'subjectid': token }
                        res = requests.post(SERVER_URL+'/pmml', headers=headers, data=pmml)
                        print res.text
                        response = json.loads(res.text)
                        transformations = SERVER_URL+'/pmml/'+response['_id']
                    else:
                        return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'al': al, 'algorithms':algorithms, 'pmmlform':pmmlform, 'uploadform':form, 'tform':tform, 'features':features, 'inputform': inputform, 'exp':True})

             #get scaling
            scaling=""
            if request.POST.get('scaling') == "scaling1":
                scaling=""
            elif request.POST.get('scaling') == "scaling2":
                scaling=SERVER_URL+'/algorithm/scaling'
            elif request.POST.get('scaling') == "scaling3":
                scaling=SERVER_URL+'/algorithm/standarization'
            #get doa
            doa=""

            #algorithms = request.session.get('alg', '')
            dataset = request.session.get('data', '')
            title= ""
            description= ""
            print json.dumps(params)

            body = {'dataset_uri': SERVER_URL+'/dataset/'+dataset, 'scaling': scaling, 'doa': doa, 'title': title, 'description':description, 'transformations':transformations, 'prediction_feature': prediction_feature, 'parameters':json.dumps(params), 'visible': False}
            print('----')
            print body
            headers = {'Accept': 'application/json', 'subjectid': token}
            res = requests.post(SERVER_URL+'/algorithm/'+algorithms, headers=headers, data=body)
            print res.text
            task_id = json.loads(res.text)['_id']
            print task_id
            #return redirect('/t_detail?name='+task_id+'&status=queued', {'token': token, 'username': username})
            res1 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
            status = json.loads(res1.text)['status']
            while (status != "COMPLETED"):
                if(status == "ERROR"):
                    error = "An error occurred while processing your request.Please try again."
                    return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'al': al, 'algorithms':algorithms, 'pmmlform':pmmlform, 'uploadform':form, 'tform':tform, 'features':features, 'inputform': inputform, 'exp':True, 'error':error})

                else:
                    res1 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
                    status = json.loads(res1.text)['status']
            #model: model/{id}
            model = json.loads(res1.text)['result']
            print model
            print dataset
            body = {'dataset_uri':SERVER_URL+'/dataset/'+dataset}
            res2 = requests.post(SERVER_URL+'/'+model, headers=headers, data=body)
            task_id = json.loads(res2.text)['_id']
            res3 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
            status = json.loads(res3.text)['status']
            print task_id
            while (status != "COMPLETED"):
                if(status == "ERROR"):
                    error = "An error occurred while processing your request.Please try again."
                    print form
                    return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'al': al, 'algorithms':algorithms, 'uploadform':form, 'pmmlform':pmmlform, 'tform':tform, 'features':features, 'inputform': inputform, 'exp':True, 'error':error})

                else:
                    res4 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
                    status = json.loads(res4.text)['status']

            new_dataset = json.loads(res4.text)['result']
            new_dataset = new_dataset.split('dataset/')[1]
            print new_dataset
            #dataset = 'jREmfXY9E997Ci'
            #model = 'aTqA637F4O00'
            res5 = requests.get(SERVER_URL+'/dataset/'+new_dataset, headers=headers)
            data_detail = json.loads(res5.text)
            res6 = requests.get(SERVER_URL+'/'+model, headers=headers)
            model_detail = json.loads(res6.text)
            predictedFeatures = model_detail['predictedFeatures']
            '''res7 = requests.get(SERVER_URL+'/dataset/'+dataset, headers=headers)
            d_detail = json.loads(res7.text)'''
            print predicted_features
            print data_detail
            if prediction_feature == "":
                prediction_feature = get_prediction_feature_of_dataset(new_dataset, token)
                print prediction_feature
            #body = { 'scaling': scaling, 'doa': doa, 'transformations':transformations, 'prediction_feature': 'https://apps.ideaconsult.net/enmtest/property/TOX/UNKNOWN_TOXICITY_SECTION/Net+cell+association/8058CA554E48268ECBA8C98A55356854F413673B/3ed642f9-1b42-387a-9966-dea5b91e5f8a', 'parameters':json.dumps(params), 'visible': False}
            #body
            print model_detail
            return render(request, "exp_dataset_detail.html", {'token': token, 'username': username, 'data_detail': data_detail, 'predicted': predictedFeatures, 'prediction':prediction_feature, 'model':model_detail, 'dataset_name':new_dataset, 'params': params })

def exp_submit(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.is_ajax():
        #queryData = request.GET.get('queryData')
        data = request.GET.get('data')
        dataset = request.GET.get('dataset_name')
        #threshold = request.GET.get('threshold')
        #print threshold
        print data
        #dataset = data['dataset_name']
        dataset = json.loads(dataset)
        #print queryData
        #dataset='ayDPMNB3JcOJAm'
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/dataset/'+dataset, headers=headers)
        prediction_feature = get_prediction_feature_of_dataset(dataset, token)
        print prediction_feature
        #import pdb;pdb.set_trace();
        d_detail = json.loads(res.text)
        print d_detail
        #import pdb;pdb.set_trace();
        data = json.loads(data)
        length = data['length']
        print length
        new = {}
        for i in range(0,int(length)):
            if data[str(i)][2] == "None":
                 new[data[str(i)][0]]= None
            else:
                new[data[str(i)][0]]= float(data[str(i)][2])
        print new
        data_Entry = []
        for det in d_detail['dataEntry']:
            name = det['compound']['name']
            det['values'][prediction_feature] = new[name]
            data_Entry.append(det)
        #d_detail contains dataset with new values
        d_detail['dataEntry']= data_Entry
        #data = json.dumps(d_detail['dataEntry'])
        data = json.dumps(d_detail)

        #data=json.dumps(data1)
        print data
        headers1 = {'content-type': 'application/json', 'subjectid':token}
        #new_data = create_dataset(d_detail['dataEntry'],"guest","", "", "")
        rows= d_detail['totalRows']
        columns = d_detail['totalColumns']
        new_data = create_dataset2( d_detail['dataEntry'], "guest", d_detail['features'], d_detail['byModel'], rows, columns)
        print new_data
        json_data = json.dumps(new_data)
        print()
        #import pdb;pdb.set_trace();
        json_data = json.dumps(json_data)
        json_data = json.loads(json_data)
        print json_data
        res = requests.post(SERVER_URL+'/dataset', headers=headers1, data=json_data, timeout=10)

        print res.text
        data = res.text.split('/dataset/')[1]
        print data
        #json_data={"dataset": data, "threshold": threshold}
        #json_data = {'dataset': data}
        json_data = json.dumps(data)
        return HttpResponse(json_data)

def exp_iter(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
        if request.method == 'GET':
            dataset = request.GET.get('dataset')
            print dataset
            headers = {'Accept': 'application/json', 'subjectid': token}
            res1 = requests.get(SERVER_URL+'/dataset/'+dataset, headers=headers)
            data_detail = json.loads(res1.text)
            model = json.loads(res1.text)['byModel']
            #model = 'A0fU5rK7B64r'
            res = requests.get(SERVER_URL+'/model/'+model, headers=headers)
            model_detail = json.loads(res.text)
            predictedFeatures = model_detail['predictedFeatures']
            algorithms = json.loads(res.text)['algorithm']['_id']
            params = json.loads(res.text)['parameters']
            if algorithms == "ocpu-expdesign-x":
                algorithms = "ocpu-expdesign-xy"
                par = {}
                for k,v in params.items():
                    if k != "newY":
                        par.update({k:v})
                params = par
            prediction_feature = get_prediction_feature_of_dataset(dataset, token)
            body = {'dataset_uri': SERVER_URL+'/dataset/'+dataset, 'scaling': "", 'doa': "", 'title': "", 'description':"", 'transformations':"", 'prediction_feature': prediction_feature, 'parameters':json.dumps(params), 'visible': False}
            print('----')
            print body
            headers = {'Accept': 'application/json', 'subjectid': token}
            #import pdb;pdb.set_trace();

            res = requests.post(SERVER_URL+'/algorithm/'+algorithms, headers=headers, data=body)
            print res.text
            task_id = json.loads(res.text)['_id']
            print task_id
            #return redirect('/t_detail?name='+task_id+'&status=queued', {'token': token, 'username': username})
            res1 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
            status = json.loads(res1.text)['status']
            while (status != "COMPLETED"):
                if(status == "ERROR"):
                    error = "An error occurred while processing your request.Please try again."
                    return render(request, "exp_dataset_detail.html", {'token': token, 'username': username, 'data_detail': data_detail, 'predicted': predictedFeatures, 'prediction':prediction_feature, 'model':model_detail, 'dataset_name':dataset, 'params': params, 'error':error })

                else:
                    res1 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
                    status = json.loads(res1.text)['status']
            #model: model/{id}
            model = json.loads(res1.text)['result']
            body = {'dataset_uri':SERVER_URL+'/dataset/'+dataset}
            res2 = requests.post(SERVER_URL+'/'+model, headers=headers, data=body)
            task_id = json.loads(res2.text)['_id']
            res3 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
            status = json.loads(res3.text)['status']

            while (status != "COMPLETED"):
                if(status == "ERROR"):
                    error = "An error occurred while processing your request.Please try again."
                    return render(request, "exp_dataset_detail.html", {'token': token, 'username': username, 'data_detail': data_detail, 'predicted': predictedFeatures, 'prediction':prediction_feature, 'model':model_detail, 'dataset_name':dataset, 'params': params, 'error':error })
                else:
                    res4 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
                    status = json.loads(res4.text)['status']

            new_dataset = json.loads(res4.text)['result']
            new_dataset = new_dataset.split('dataset/')[1]
            print new_dataset
            res5 = requests.get(SERVER_URL+'/dataset/'+new_dataset, headers=headers)
            data_detail = json.loads(res5.text)
            res6 = requests.get(SERVER_URL+'/'+model, headers=headers)
            model_detail = json.loads(res6.text)
            predictedFeatures = model_detail['predictedFeatures']
            res7 = requests.get(SERVER_URL+'/dataset/'+dataset, headers=headers)
            d_detail = json.loads(res7.text)
            prediction_feature = get_prediction_feature_of_dataset(new_dataset, token)
            print data_detail
            #body = { 'scaling': scaling, 'doa': doa, 'transformations':transformations, 'prediction_feature': 'https://apps.ideaconsult.net/enmtest/property/TOX/UNKNOWN_TOXICITY_SECTION/Net+cell+association/8058CA554E48268ECBA8C98A55356854F413673B/3ed642f9-1b42-387a-9966-dea5b91e5f8a', 'parameters':json.dumps(params), 'visible': False}
            #body
            return render(request, "exp_dataset_detail.html", {'token': token, 'username': username, 'data_detail': data_detail,'d_detail':d_detail, 'predicted': predictedFeatures, 'prediction':prediction_feature, 'model':model_detail, 'dataset_name':new_dataset, 'params':params})


#Experimental design without input
def exp_design(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')

    if request.method == 'GET':
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/algorithm/ocpu-expdesign-noxy', headers=headers)
        print json.loads(res.text)
        al = json.loads(res.text)

        return render(request, "ocpu_params.html", {'token': token, 'username': username, 'al':al })

    if request.method == 'POST':

        pform = ExperimentalParamsForm(request.POST)
        if not pform.is_valid():
            return render(request, "ocpu_params.html", {'token': token, 'username': username, 'pform':pform })
        else:
            headers = {'Accept': 'application/json', 'subjectid': token}
            res = requests.get(SERVER_URL+'/algorithm/ocpu-expdesign-noxy', headers=headers)
            al = json.loads(res.text)
            parameters = request.POST.getlist('parameters')

            params, al = get_params(request, parameters, al)

            body = {'parameters':json.dumps(params), 'visible':False }
            headers = {'Accept': 'application/json', 'subjectid': token}
            res = requests.post(SERVER_URL+'/algorithm/ocpu-expdesign-noxy', headers=headers, data=body)
            print res.text
            task_id = json.loads(res.text)['_id']
            print task_id
            res1 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
            status = json.loads(res1.text)['status']
            while (status != "COMPLETED"):
                if(status == "ERROR"):
                    error = "An error occurred while processing your request.Please try again."
                    return render(request, "ocpu_params.html", {'token': token, 'username': username, 'pform':pform, 'error':error, 'al':al })
                else:
                    res1 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
                    status = json.loads(res1.text)['status']
            #model: model/{id}
            model = json.loads(res1.text)['result']
            res2 = requests.post(SERVER_URL+'/'+model, headers=headers)
            task_id = json.loads(res2.text)['_id']
            res3 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
            status = json.loads(res3.text)['status']

            while (status != "COMPLETED"):
                if(status == "ERROR"):
                    error = "An error occurred while processing your request.Please try again."
                    return render(request, "ocpu_params.html", {'token': token, 'username': username, 'pform':pform, 'error':error, 'al':al })
                else:
                    res4 = requests.get(SERVER_URL+'/task/'+task_id, headers=headers)
                    status = json.loads(res4.text)['status']

            dataset = json.loads(res4.text)['result']
            dataset = dataset.split('dataset/')[1]

            return redirect('/data_detail?name='+dataset, {'token': token, 'username': username})


#Interlab testing select substance owners
def interlab_select_substance(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
        else:
            page=request.GET.get('page')
            if page:
                headers = {'Accept': 'application/json', 'subjectid': token}
                page1=str(int(page)-1)
                res = requests.get('https://apps.ideaconsult.net:443/enmtest/substanceowner?page='+page1+'&pagesize=20', headers=headers)
                substance_owner=json.loads(res.text)
                substance_owner = substance_owner['facet']
            else:
                headers = {'Accept': 'application/json', 'subjectid': token}
                page=1
                res = requests.get('https://apps.ideaconsult.net:443/enmtest/substanceowner?page=0&pagesize=20', headers=headers)
                substance_owner=json.loads(res.text)
                substance_owner = substance_owner['facet']
    if request.method == 'GET':
        form = SubstanceownerForm(initial={'substanceowner': ''})
        if len(substance_owner)<20:
            last=page
            return render(request, "interlab_substance.html", {'token': token, 'username': username, 'form':form, 'substance_owner': substance_owner, 'page': page, 'last':last,})
        else:
            return render(request, "interlab_substance.html", {'token': token, 'username': username, 'form':form, 'substance_owner': substance_owner, 'page': page})
    if request.method == 'POST':
        method = request.POST.get('radio_method')

        substance_owner = request.POST.get('radio')
        if not substance_owner:
            form = SubstanceownerForm(initial={'substanceowner': ''})
            page=request.GET.get('page')
            if page:
                headers = {'Accept': 'application/json', 'subjectid': token}
                page1=str(int(page)-1)
                res = requests.get('https://apps.ideaconsult.net:443/enmtest/substanceowner?page='+page1+'&pagesize=20', headers=headers)
                substance_owner=json.loads(res.text)
                substance_owner = substance_owner['facet']
            else:
                headers = {'Accept': 'application/json', 'subjectid': token}
                page=1
                res = requests.get('https://apps.ideaconsult.net:443/enmtest/substanceowner?page=0&pagesize=20', headers=headers)
                substance_owner=json.loads(res.text)
                substance_owner = substance_owner['facet']
                error = "Please select substance owner."
                return render(request, "interlab_substance.html", {'token': token, 'username': username, 'form':form, 'substance_owner': substance_owner, 'page': page, 'error':error})
        else:
            substance_owner = 'https://apps.ideaconsult.net/enmtest/substanceowner/'+substance_owner
            request.session['substanceowner']= substance_owner
            headers = {'Accept': 'application/json', 'subjectid': token}
            res = requests.get(substance_owner+'/substance', headers=headers)
            substances=json.loads(res.text)
            request.session['substances'] = substances
            return redirect('/interlab_params', {'token': token, 'username': username})

def interlab_params(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    if request.method == 'GET':
        #dataset=request.GET.get('dataset')
        form=InterlabForm()
        dataset = "8aj1O7Vny4uJLl"
        return render(request, "interlab_params.html", {'token': token, 'username': username, 'dataset':dataset, 'form':form})
    if request.method == 'POST':
        dataset=request.GET.get('dataset')
        form = InterlabForm(request.POST)
        if not form.is_valid():
            return render(request, "interlab_params.html", {'token': token, 'username': username, 'dataset':dataset, 'form':form})
        modelname = form['modelname'].value()
        description = form['description'].value()
        dataset = "http://test.jaqpot.org:8080/jaqpot/services/dataset/interlab"
        prediction = "https://apps.ideaconsult.net/enmtest/property/TOX/UNKNOWN_TOXICITY_SECTION/Log2+transformed/94D664CFE4929A0F400A5AD8CA733B52E049A688/3ed642f9-1b42-387a-9966-dea5b91e5f8a"
        headers = {'Accept': 'application/json', 'subjectid': token}
        body = {'title': modelname, 'descriptions': description, 'dataset_uri': dataset, 'prediction_feature':prediction}
        res = requests.post(SERVER_URL+'/interlab/test', headers=headers, data=body)
        print json.loads(res.text)['_id']
        return redirect('/report?name='+json.loads(res.text)['_id'])


def clean_dataset(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    if request.method == 'GET':
        dataset = request.GET.get('dataset')
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/dataset/ayDPMNB3JcOJAm', headers=headers)
        data= json.loads(res.text)
        prediction_feature = get_prediction_feature_of_dataset(dataset, token)
        suggested=""
        for d in data['features']:
            if d['name']=='suggestedTrials':
                suggested= d['uri']
        new_data = create_and_clean_dataset(data, prediction_feature, suggested)
        json_data = json.dumps(new_data)
        print json_data
        headers1 = {'Content-type': 'application/json', 'subjectid': token}
        res = requests.post(SERVER_URL+'/dataset', headers=headers1, data=json_data)
        dataset = res.text.split('/dataset/')[1]
        print dataset
        return redirect('/dataset?dataset=' +dataset)

#List of reports
def report_list(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')

    page = request.GET.get('page')
    last = request.GET.get('last')
    if request.method == 'GET':
        report=[]
        headers = {'Accept': 'application/json', 'subjectid': token}
        #get total number of datasets
        res = requests.get(SERVER_URL+'/report?start=0&max=20', headers=headers)
        total_reports= int(res.headers.get('total'))
        if total_reports%20 == 0:
            last = total_reports/20
        else:
            last = (total_reports/20)+1

        if page:
            #page1 is the number of first dataset of page
            page1=int(page) * 20 - 20
            k=str(page1)
            if page1 <= 1:
                res = requests.get(SERVER_URL+'/report?start=0&max=20', headers=headers)
            else:
                res = requests.get(SERVER_URL+'/report?start='+k+'&max=20', headers=headers)
        else:
            page = 1
            res = requests.get(SERVER_URL+'/report?start=0&max=20', headers=headers)
        data= json.loads(res.text)
        for d in data:
            report.append({'id':d['_id'], 'meta':d['meta']})

        return render(request, "reports.html", {'token': token, 'username': username, 'report': report, 'page': page, 'last':last})

#Display details of each dataset
'''def dataset_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')

    name = request.GET.get('name', '')
    page = request.GET.get('page', '')
    data_detail, last, page = paginate_dataset(request, name, token, username, page)
    if data_detail and last and page:
            a=[]
            #a=collections.OrderedDict()
            # a contains all compound's properties
            for key in data_detail['dataEntry']:
                for k, value in key.items():
                    if k =='values':
                        counter=0
                        for m,n in value.items():
                            if m not in a:
                                a.append(m)


            print a
            properties={}
            new=[]
            compound = []
            for i in range(len(a)):
                for k in data_detail['features']:
                    if k['uri'] == a[i]:
                        new.append(k)

            #get response json
            for key in data_detail['dataEntry']:
                properties[key['compound']['URI']] = []
                properties[key['compound']['URI']].append({"compound": key['compound']['URI']})
                properties[key['compound']['URI']].append({"name": key['compound']['name']})

                #for each compound
                for k, value in key.items():
                    if k =='values':
                        for i in range(len(a)):
                            #if a compound haven't value for a property add its value Null
                            if a[i] in value:
                                properties[key['compound']['URI']].append({"prop": a[i], "value": value[a[i]]})
                            else:
                                properties[key['compound']['URI']].append({"prop":  a[i], "value": "NULL"})

            return render(request, "dataset_detail.html", {'token': token, 'username': username, 'name': name, 'data_detail':data_detail, 'properties': properties, 'a': a, 'new': new, 'page':page, 'last':last})'''

#Delete selected report
def report_delete(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    else:
        return redirect('/login')
    id = request.GET.get('id')
    #delete report
    headers = {'Accept': 'application/json', "subjectid": token}
    res = requests.delete(SERVER_URL+'/report/'+id, headers=headers)
    reply = res.text
    print reply
    return redirect('/reports')