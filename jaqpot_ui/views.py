import os
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from jaqpot_ui.forms import UserForm, BibtexForm, TrainForm, FeatureForm, ContactForm, SubstanceownerForm, UploadFileForm
import requests
import json
import datetime
import subprocess
from settings import EXT_AUTH_URL_LOGIN, EXT_AUTH_URL_LOGOUT, EMAIL_HOST_USER, SERVER_URL
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from jaqpot_ui.templatetags import templates_extras
import jsonpatch
import xmltodict


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
    #else go to tasks
    all_tasks = []
    #get all tasks with status Running
    headers = {'Accept': 'text/uri-list', 'subjectid': token}
    headers = {'Accept': 'application/json', 'subjectid': token}
    res = requests.get(SERVER_URL+'/task?creator='+username+'&status=RUNNING&start=0&max=10000', headers=headers)
    list_resp = json.loads(res.text)
    if res.status_code == 200:
        list_run=[]

        for l in list_resp:
            list_run.append({'name': l['_id'], 'status': "running", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "running", 'meta': l['meta']})
        list_run = json.dumps(list_run)
        list_run = json.loads(list_run)

        #get all tasks with status Completed
        res = requests.get(SERVER_URL+'/task?status=COMPLETED&creator='+username+'&start=0&max=10000', headers=headers)
        list_resp = json.loads(res.text)

        list_complete=[]
        for l in list_resp:
            list_complete.append({'name': l['_id'], 'status': "completed", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "completed", 'meta': l['meta']})
        list_complete= json.dumps(list_complete)
        list_complete = json.loads(list_complete)

        #get all tasks with status Cancelled
        res = requests.get(SERVER_URL+'/task?status=CANCELLED&creator='+username+'&start=0&max=10000', headers=headers)
        list_resp = json.loads(res.text)

        list_cancelled=[]
        for l in list_resp:

            list_cancelled.append({'name': l['_id'], 'status': "cancelled", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "cancelled", 'meta': l['meta']})
        list_cancelled= json.dumps(list_cancelled)
        list_cancelled = json.loads(list_cancelled)

        #get all tasks with status Error
        res = requests.get(SERVER_URL+'/task?status=ERROR&creator='+username+'&start=0&max=10000', headers=headers)
        list_resp = json.loads(res.text)

        list_error=[]
        for l in list_resp:

            list_error.append({'name': l['_id'], 'status': "error", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "error", 'meta': l['meta']})
        list_error= json.dumps(list_error)
        list_error = json.loads(list_error)


        #get all tasks with status Queued
        res = requests.get(SERVER_URL+'/task?status=QUEUED&creator='+username+'&start=0&max=10000', headers=headers)
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
    status = request.GET.get('status')
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

        '''g = Graph().parse(URL+'/task/'+name)
        output = {}
        k=''
        for s, p, o in g:
            if type(o) == rdflib.term.Literal:
                if 'elements/1.1/' in p:
                    k = p.split('elements/1.1/')[1]
                    print k
                if '#' in p:
                    k = p.split('#')[1]
                    print k
                output.update({k: o.toPython()})'''


        #output = json.dumps(res.text)
        output = json.loads(res.text)
        if output['meta']['date']:
            date=output['meta']['date'].split('T')[0]
            output['meta']['date'] = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%y')

        return render(request, "taskdetail.html", {'token': token, 'username': username, 'name': name, 'status': status, 'output': output})

#stop running task
def stop_task(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
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

    if request.method == 'GET':
        final_output=[]
        #get all bibtex
        headers = {'Accept': 'application/json', 'subjectid': token}
        headers1 = {'Accept': 'text/uri-list', 'subjectid': token}
        res = requests.get(SERVER_URL+'/bibtex?bibtype=Entry&creator='+username+'&&&start=0&max=10000', headers=headers1)
        list_resp = res.text
        if res.status_code == 403:
            error = "This request is forbidden (e.g., no authentication token is provided)"
            return render(request, "bibtex.html",{'token': token, 'username': username, 'name': name, 'error': error})
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

    if request.method == 'GET':
        return render(request, "bibdetail.html", {'token': token, 'username': username, 'name': name})

#User interface
def user(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')

    if request.method == 'GET':
        #curl command for getting user info
        #curl -X GET http://enanomapper.ntua.gr:8880/jaqpot/services/user/hampos -H "Content-type: application/json" -H "Accept: application/json" -H subjectid:AQIC5wM2LY4SfcwVYB0lR6oY-G37NauRX4VvIGegOod7F_g.*AAJTSQACMDE.*
        #headers = {'content-type': 'text/uri-list'}
        #r = requests.get('http://opentox.informatik.tu-muenchen.de:8080/OpenTox-dev/model', headers=headers)
        #print r.text
        headers = {'content-type': 'application/json', 'subjectid': token}
        #headers = {'subjectid': token}
        res = requests.get(SERVER_URL+'/user/'+ username, headers=headers)
        #rw=requests.get('http://opentox.ntua.gr:8080/user/'+ username +'@opensso.in-silico.ch/quota', headers=headers)
        print res.text
        contacts = json.loads(res.text)
        res1 = requests.get(SERVER_URL+'/user/'+ username+'/quota', headers=headers)
        print res1.text
        percentage = json.loads(res1.text)
        percentage = json.dumps(percentage)
        #contacts = {'name': username, 'maxtasks': 5, 'maxmodels': 2000, 'maxalgorithms': 2000, 'models': 100, 'tasks':2, 'alg': 1000}
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
    if request.method == 'GET':
        dataset=[]
        headers = {'Accept': 'application/json', 'subjectid': token}

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
            dataset.append({'name': d['_id'], 'meta': d['meta']})
        if len(dataset)< 20:
            last= page

        return render(request, "choose_dataset.html", {'token': token, 'username': username, 'entries2': dataset, 'page': page, 'last':last})


def choose_dataset(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
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
        request.session['alg'] = algorithms[0]['alg']
        request.session['data'] = dataset
        return redirect('/change_params', {'token': token, 'username': username,})

def change_params(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.method == 'GET':
        form = UploadFileForm()
        dataset = request.session.get('data', '')
        algorithms = request.session.get('alg', '')
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/algorithm/'+algorithms, headers=headers)
        al = json.loads(res.text)
        headers1 = {'Accept': 'text/uri-list', 'subjectid': token}
        res1 = requests.get(SERVER_URL+'/pmml/?start=0&max=10', headers=headers1)
        pmml=res1.text
        pmml = pmml.splitlines()
        return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'al': al, 'algorithms':algorithms, 'pmml': pmml,'uploadform':form})
    if request.method == 'POST':
        #get transformations
        transformations=""
        if request.POST.get('radio_pmml') == "none":
            transformations = ""
        elif request.POST.get('radio_pmml') == "pm":
            transformations = request.POST.get('pmml_file')
            print transformations
        elif request.POST.get('radio_pmml') == "input":
            print('---')
        elif request.POST.get('radio_pmml') == "file":
            form = UploadFileForm(request.POST, request.FILES)
            content=[]
            if form.is_valid:
                pmml= request.FILES['file'].read()
                '''for chunk in request.FILES['file'].chunks():
                    content.append(chunk)
                content=json.dumps(content)
                print content'''
                headers = {'Content-Type': 'application/xml',  'subjectid': token}
                res = requests.post(SERVER_URL+'/pmml', headers=headers, data=pmml)
                print res.text

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
        elif request.POST.get('scaling') == "doa2":
            doa=SERVER_URL+'/algorithm/leverage'
        elif request.POST.get('scaling') == "doa3":
            doa=SERVER_URL+'/algorithm/leverage'
        algorithms = request.session.get('alg', '')
        dataset = request.session.get('data', '')

        body = {'dataset_uri': SERVER_URL+'/dataset/'+dataset, 'scaling':scaling, 'doa': doa, 'transformations':transformations, 'prediction_feature': 'https://apps.ideaconsult.net/enmtest/property/TOX/UNKNOWN_TOXICITY_SECTION/Log2+transformed/94D664CFE4929A0F400A5AD8CA733B52E049A688/3ed642f9-1b42-387a-9966-dea5b91e5f8a'}
        headers = {'Accept': 'application/json', 'subjectid': token}
        #res = requests.post(SERVER_URL+'/algorithm/'+algorithms, headers=headers, data=body)
        #print res.text

        print request.POST
        print request.POST.get('file')
        print request.POST.getlist('radio_pmml')
        print request.POST.getlist('checkbox')
        print request.POST.getlist('select')
        return redirect('/task', {'token': token, 'username': username})


#Conformer
def conformer(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.method == 'GET':
        return render(request, "conformer.html", {'token': token, 'username': username})
    if request.method == 'POST':
        #add task for descriptors calculation
        return redirect('/task', {'token': token, 'username': username})

def model(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        #validate token
        #if token is not valid redirect to login page
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    if request.method == 'GET':
        #get all models
        #headers = {'Accept:text/uri-list'}
        #r = requests.get('http://opentox.informatik.tu-muenchen.de:8080/OpenTox-dev/model', headers=headers)
        #print r.text
        models = []
        #get all models
        headers = {'Accept': 'text/uri-list', "subjectid": token}
        res = requests.get(SERVER_URL+'/model?start=0&max=10000', headers=headers)
        list_resp = res.text
        #get each line
        list_resp = list_resp.splitlines()
        for l in list_resp:
            l = l.split('/model/')[1]
            models.append({'name': l})
        models = json.dumps(models)
        models = json.loads(models)

        #models= [{'name':'model1'}, {'name':'model2'}, {'name':'model3'}, {'name':'model4'}]
        return render(request, "model.html", {'token': token, 'username': username, 'models':models })

def model_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    #details = [{'a':'0.1','b':'0.2', 'description':'model'}]
    #get task details in rdf format
    headers = {'Accept': 'application/json', "subjectid": token}
    res = requests.get(SERVER_URL+'/model/'+name, headers=headers)
    details = json.loads(res.text)
    print res.text


    if request.method == 'GET':
        return render(request, "model_detail.html", {'token': token, 'username': username, 'details':details, 'name':name })

def model_pmml(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    headers = {'Accept': 'application/xml', "subjectid": token}
    res = requests.get(SERVER_URL+'/model/'+name+'/pmml', headers=headers)
    #details = json.loads(res.text)
    pmml = res.text
    response = HttpResponse(pmml, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="pmml_'+name+'.xml"'
    return response


def features(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    page = request.GET.get('page')
    last = request.GET.get('last')

    if request.method == 'GET':
        headers = {'Accept': 'application/json', 'subjectid': token}
        if page:
            page1=int(page) * 20 - 20
            k=str(page1)
            if page1 <= 1:
                res = requests.get(SERVER_URL+'/feature?creator='+username+'&&start=0&max=20', headers=headers)
            elif last:
                res = requests.get(SERVER_URL+'/feature?creator='+username+'&&start='+last+'&max=20', headers=headers)
            else:
                res = requests.get(SERVER_URL+'/feature?creator='+username+'&&start='+k+'&max=20', headers=headers)

        else:
            page = 1
            res = requests.get(SERVER_URL+'/feature?creator='+username+'&&start=0&max=20', headers=headers)
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

def feature_details(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
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
    id = request.GET.get('id')
    if request.method == 'GET':
        #delete bibtex
        headers = {'content-type': 'text/uri-list', 'subjectid': token}
        res = requests.delete(SERVER_URL+'/feature/'+id, headers=headers)
        return render(request, "mainPage.html", {'token': token, 'username': username })


def algorithm(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

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

def algorithm_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
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
    id = request.GET.get('id')
    if request.method == 'GET':
        #delete algorithm
        headers = {'content-type': 'text/uri-list', 'subjectid': token}
        res = requests.delete(SERVER_URL+'/algorithm/'+id, headers=headers)
        return render(request, "mainPage.html", {'token': token, 'username': username})


def dataset(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    page = request.GET.get('page')
    last = request.GET.get('last')
    dataset=[]
    if request.method == 'GET':
        dataset=[]
        headers = {'Accept': 'application/json', 'subjectid': token}

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
            dataset.append({'name': d['_id'], 'meta': d['meta']})
        if len(dataset)< 20:
            last= page

        return render(request, "dataset.html", {'token': token, 'username': username, 'dataset': dataset, 'page': page, 'last':last})


def dataset_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name', '')
    if request.method == 'GET':
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(SERVER_URL+'/dataset/'+name, headers=headers)
        data_detail=json.loads(res.text)
        properties=[]
        a=[]
        # a contains all compound's properties
        for key in data_detail['dataEntry']:
            for k, value in key.items():
                if k !='compound':
                    for m,n in value.items():
                        if m not in a:
                            a.append(m)
        properties={}
        #get response json
        for key in data_detail['dataEntry']:
            properties[key['compound']['URI']] = []
            properties[key['compound']['URI']].append({"compound": key['compound']['URI']})
            #for each compound
            for k, value in key.items():
                if k !='compound':
                    for i in range(len(a)):
                        #if a compound haven't value for a property add its value Null
                        if a[i] in value:
                            properties[key['compound']['URI']].append({"prop": a[i], "value": value[a[i]]})
                        else:
                            properties[key['compound']['URI']].append({"prop": a[i], "value": "NULL"})

        return render(request, "dataset_detail.html", {'token': token, 'username': username, 'name': name, 'data_detail': data_detail, 'properties': properties, 'a': a})
#Predict model
def predict(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    #Get the current page
    page = request.GET.get('page')
    #Get the last page
    last = request.GET.get('last')
    #Check if user is authenticated. Else redirect to login page
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    if request.method == 'GET':
        dataset=[]
        headers = {'Accept': 'application/json', 'subjectid': token}
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
            dataset.append({'name': d['_id']})
        if len(dataset)< 20:
            last= page
        #Display all datasets for selection
        return render(request, "predict.html", {'token': token, 'username': username, 'dataset': dataset, 'page': page, 'last':last})

def predict_model(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

    my_models = [{'name':'model1'}, {'name':'model2'}, {'name':'model3'}, {'name':'model4'}]
    my_models = json.dumps(my_models)
    my_models = json.loads(my_models)
    if request.method == 'GET':
        #Get the selected dataset for prediction
        dataset = request.GET.get('dataset')
        #Save selected dataset at session dataset
        request.session['dataset'] = dataset
        models = []
        #get all models
        headers = {'Accept': 'text/uri-list', "subjectid": token}
        res = requests.get(SERVER_URL+'/model?start=0&max=10000', headers=headers)
        list_resp = res.text
        #get each line
        list_resp = list_resp.splitlines()
        for l in list_resp:
            l = l.split('/model/')[1]
            models.append({'name': l})
        models = json.dumps(models)
        models = json.loads(models)
        #Display all models for selection
        return render(request, "predict_model.html", {'token': token, 'username': username, 'my_models': models})
    if request.method == 'POST':
        #Get the selected dataset for prediction from session
        dataset= request.session.get('dataset', '')
        #Get the selected model
        selected_model = request.POST.get('radio')
        headers = {'Accept': 'application/json', "subjectid": token}
        res = requests.post(SERVER_URL+'/model/'+selected_model, headers=headers, data=SERVER_URL+'/dataset/'+dataset)
        response = json.loads(res.text)
        task = response['_id']
        #Redirect to the produced task
        return render(request, "new_task.html", {'token': token, 'username': username, 'task': task})

#Contact form
def contact(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

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
    if request.method == 'GET':
        return render(request, "thanks.html", {'token': token, 'username': username})

def compound(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.method == 'GET':
        compound= [{'name':'compound1'}, {'name':'compound2'}, {'name':'compound3'}, {'name':'compound4'}]
        return render(request, "compound.html", {'token': token, 'username': username, 'compound': compound})

def compound_details(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name', '')
    if request.method == 'GET':
        return render(request, "compound_detail.html", {'token': token, 'username': username, 'name': name})

#redirect to source page
def source(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.method == 'GET':
        return render(request, "source.html", {'token': token, 'username': username})

#redirect to documentation page
def documentation(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.method == 'GET':
        return render(request, "documentation.html", {'token': token, 'username': username})

def explore(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
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
    if request.method == 'GET':
        form = SubstanceownerForm(initial={'substanceowner': ''})
        return render(request, "substance.html", {'token': token, 'username': username, 'form':form})
    if request.method == 'POST':
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
            return render(request, "substance.html", {'token': token, 'username': username, 'form':form})

def select_substance(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.is_ajax():
            checkall = request.GET('checkall')
            print checkall
            print('is ajax')
            return HttpResponse(checkall)
    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
        if request.method == 'GET':
            substances = request.session.get('substances', '')
            return render(request, "select_substance.html", {'token': token, 'username': username, 'substances':substances['substance']})
        '''if request.is_ajax():
                checkall = request.GET('checkall')
                print checkall
                print('is ajax')
                return HttpResponse(checkall)'''
        if request.method == 'POST':
            sub= request.POST.getlist('checkbox')
            request.session['selected_substances'] = sub
            print sub
            headers = {'Accept': 'application/json', 'subjectid': token}
            res1 = requests.get(SERVER_URL+'/enm/property/categories', headers=headers)
            properties=json.loads(res1.text)
            print properties
            request.session['properties'] = properties
            return redirect('/properties', {'token': token, 'username': username})
            #return render(request, "properties.html", {'token': token, 'username': username})

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

def select_descriptors(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

    if token:
        r = requests.post(SERVER_URL + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
        if request.method == 'GET':
            headers = {'Accept': 'application/json', 'subjectid': token}
            res1 = requests.get(SERVER_URL+'/enm/descriptor/categories', headers=headers)
            descriptors=json.loads(res1.text)
            print descriptors
            return render(request, "descriptors.html", {'token': token, 'username': username, 'descriptors':descriptors})
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
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

