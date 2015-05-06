from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
import rdflib
from jaqpot_ui.forms import UserForm, BibtexForm, TrainForm, FeatureForm, ContactForm
import requests
import json
import datetime
import subprocess
from settings import EXT_AUTH_URL_LOGIN, EXT_AUTH_URL_LOGOUT, URL, EMAIL_HOST_USER, URL_1
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from rdflib import Graph, plugin, term
from rdflib.serializer import Serializer
from jaqpot_ui.templatetags import templates_extras
import jsonpatch


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
            r = requests.post(URL_1 + '/aa/login', data={'username': username, 'password': password})
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
        r = requests.post(URL_1 + '/aa/logout', headers={'subjectid': token})
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
        r = requests.post(URL_1 + '/aa/validate', headers={'subjectid': token})
        if r.status_code != 200:
            return redirect('/login')
    #else go to tasks
    all_tasks = []
    #get all tasks with status Running
    headers = {'Accept': 'text/uri-list', 'subjectid': token}
    headers = {'Accept': 'application/json', 'subjectid': token}
    res = requests.get(URL_1+'/task?creator='+username+'&status=RUNNING&start=0&max=10000', headers=headers)
    list_resp = json.loads(res.text)
    if res.status_code == 200:
        list_run=[]

        for l in list_resp:
            list_run.append({'name': l['_id'], 'status': "running", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "running", 'meta': l['meta']})
        list_run = json.dumps(list_run)
        list_run = json.loads(list_run)

        #get all tasks with status Completed
        res = requests.get(URL_1+'/task?status=COMPLETED&creator='+username+'&start=0&max=10000', headers=headers)
        list_resp = json.loads(res.text)

        list_complete=[]
        for l in list_resp:
            list_complete.append({'name': l['_id'], 'status': "completed", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "completed", 'meta': l['meta']})
        list_complete= json.dumps(list_complete)
        list_complete = json.loads(list_complete)

        #get all tasks with status Cancelled
        res = requests.get(URL_1+'/task?status=CANCELLED&creator='+username+'&start=0&max=10000', headers=headers)
        list_resp = json.loads(res.text)

        list_cancelled=[]
        for l in list_resp:

            list_cancelled.append({'name': l['_id'], 'status': "cancelled", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "cancelled", 'meta': l['meta']})
        list_cancelled= json.dumps(list_cancelled)
        list_cancelled = json.loads(list_cancelled)

        #get all tasks with status Error
        res = requests.get(URL_1+'/task?status=ERROR&creator='+username+'&start=0&max=10000', headers=headers)
        list_resp = json.loads(res.text)

        list_error=[]
        for l in list_resp:

            list_error.append({'name': l['_id'], 'status': "error", 'meta': l['meta']})
            all_tasks.append({'name': l['_id'], 'status': "error", 'meta': l['meta']})
        list_error= json.dumps(list_error)
        list_error = json.loads(list_error)


        #get all tasks with status Queued
        res = requests.get(URL_1+'/task?status=QUEUED&creator='+username+'&start=0&max=10000', headers=headers)
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
        res = requests.get(URL_1+'/task/'+name, headers=headers)
        data = json.loads(res.text)
        if data['meta']['date']:
            date=data['meta']['date'].split('T')[0]
            data['meta']['date'] = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%y')
        data = json.dumps(data)
        return HttpResponse(data)

    if request.method == 'GET':
        #get task details in rdf format
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(URL_1+'/task/'+name, headers=headers)

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
        res = requests.delete(URL_1+'/task/'+id, headers=headers)
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
        res = requests.get(URL_1+'/bibtex?bibtype=Entry&creator='+username+'&&&start=0&max=10000', headers=headers1)
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
        res = requests.patch(url=URL_1+'/bibtex/'+id, data=body, headers=headers)
        print res.text
        return HttpResponse(res.text)


    if request.method == 'GET':
        #send request
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(URL_1+'/bibtex/'+id, headers=headers)
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
        res = requests.delete(URL_1+'/bibtex/'+id, headers=headers)
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
        res = requests.post(URL_1+'/bibtex', data = bibtex_entry, headers=headers)
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
        res = requests.get(URL_1+'/user/'+ username, headers=headers)
        #rw=requests.get('http://opentox.ntua.gr:8080/user/'+ username +'@opensso.in-silico.ch/quota', headers=headers)
        print res.text
        contacts = json.loads(res.text)
        #print rw.text
        #contacts = {'name': username, 'maxtasks': 5, 'maxmodels': 2000, 'maxalgorithms': 2000, 'models': 100, 'tasks':2, 'alg': 1000}
        contacts = json.dumps(contacts)

        return render(request, "user_details.html", {'token': token, 'username': username, 'name': name, 'contacts': contacts})

def trainmodel(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    page = request.GET.get('page')
    last = request.GET.get('last')

    if request.method == 'GET':
        #headers = {'Accept': 'text/uri-list', 'subjectid': token}
        #res = requests.get('http://enanomapper.ntua.gr:8880/jaqpot/services/dataset?start=0&max=10', headers=headers)
        entries = [ "data", "data2", "data3","data4", "data5", "data6",]
        dataset=[]
        headers = {'Accept': 'application/json', 'subjectid': token}

        if page:
            page1=int(page) * 20 - 20
            k=str(page1)
            if page1 <= 1:
                res = requests.get(URL_1+'/dataset?start=0&max=20', headers=headers)
            elif last:
                res = requests.get(URL_1+'/dataset?start='+last+'&max=20', headers=headers)
            else:
                res = requests.get(URL_1+'/dataset?start='+k+'&max=20', headers=headers)

        else:
            page = 1
            res = requests.get(URL_1+'/dataset?start=0&max=20', headers=headers)
        data= json.loads(res.text)
        for d in data:
            dataset.append({'name': d['_id']})
        if len(dataset)< 20:
            last= page

        return render(request, "choose_dataset.html", {'token': token, 'username': username, 'entries': entries , 'entries2': dataset, 'page': page, 'last':last})


def choose_dataset(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    form = TrainForm(initial={})
    if request.method == 'GET':
        dataset = request.GET.get('dataset')
        headers = {'Accept': 'text/uri-list', 'subjectid': token}
        algorithms = []
        res = requests.get(URL_1+'/algorithm?start=0&max=10', headers=headers)
        list_resp = res.text
        list_resp = list_resp.split('\n')[:-1]
        for l in list_resp:
            l = l.split('/algorithm/')[1]
            algorithms.append({'name': l})
        algorithms = json.dumps(algorithms)
        algorithms = json.loads(algorithms)
        entries_2 = [ "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8"]
        entries_3 = [ "1", "2", "3", "4", "5", "6", "7", "8" ]
        return render(request, "train_model.html", {'token': token, 'username': username, 'entries': algorithms, 'entries_2': entries_2, 'entries_3': entries_3, 'form':form, 'dataset': dataset})
    if request.method == 'POST':
        algorithms=[]
        for alg in request.POST.getlist('checkbox'):
            headers = {'Accept': 'application/json', 'subjectid': token}
            res = requests.get(URL_1+'/algorithm/'+alg, headers=headers)
            info = json.loads(res.text)
            algorithms.append({"alg":alg, "info": info})
        algorithms = json.dumps(algorithms)
        print algorithms
        dataset = request.GET.get('dataset')
        #alg_param = [{'alg':'svm ', 'kernel': 'rdf', 'gamma':0.5, 'e':0.1},{'alg':'svm ', 'kernel': 'rdf', 'gamma':0.5, 'e':0.1}]
        alg_param = [{'alg':'svm ', 'kernel': 'rdf', 'gamma': 0.5, 'e': 0.1}]
        print dataset
        return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'alg_param': alg_param, 'algorithms': algorithms})

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
        r = requests.post(URL_1 + '/aa/validate', headers={'subjectid': token})
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
        res = requests.get(URL_1+'/model?start=0&max=10000', headers=headers)
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
    res = requests.get(URL_1+'/model/'+name, headers=headers)
    details = json.loads(res.text)
    print res.text


    if request.method == 'GET':
        return render(request, "model_detail.html", {'token': token, 'username': username, 'details':details, 'name':name })

def model_pmml(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    headers = {'Accept': 'application/xml', "subjectid": token}
    res = requests.get(URL_1+'/model/'+name+'/pmml', headers=headers)
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
                res = requests.get(URL_1+'/feature?creator='+username+'&&start=0&max=20', headers=headers)
            elif last:
                res = requests.get(URL_1+'/feature?creator='+username+'&&start='+last+'&max=20', headers=headers)
            else:
                res = requests.get(URL_1+'/feature?creator='+username+'&&start='+k+'&max=20', headers=headers)

        else:
            page = 1
            res = requests.get(URL_1+'/feature?creator='+username+'&&start=0&max=20', headers=headers)
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
        res = requests.get(URL_1+'/feature/'+name, headers=headers)
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
        res = requests.delete(URL_1+'/feature/'+id, headers=headers)
        return render(request, "mainPage.html", {'token': token, 'username': username })


def algorithm(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

    if request.method == 'GET':
         algorithms = []
         #get all algorithms
         headers = {'Accept': 'text/uri-list', 'subjectid': token}
         res = requests.get(URL_1+'/algorithm?start=0&max=10', headers=headers)
         list_resp = res.text
         list_resp = list_resp.split('\n')[:-1]
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
        res = requests.get(URL_1+'/algorithm/'+algorithm, headers=headers)
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
        res = requests.delete(URL_1+'/algorithm/'+id, headers=headers)
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
                res = requests.get(URL_1+'/dataset?start=0&max=20', headers=headers)
            elif last:
                res = requests.get(URL_1+'/dataset?start='+last+'&max=20', headers=headers)
            else:
                res = requests.get(URL_1+'/dataset?start='+k+'&max=20', headers=headers)

        else:
            page = 1
            res = requests.get(URL_1+'/dataset?start=0&max=20', headers=headers)
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
        res = requests.get(URL_1+'/dataset/'+name, headers=headers)
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

def predict(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

    if request.method == 'GET':
        return render(request, "predict.html", {'token': token, 'username': username})

def predict_model(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    my_models = [{'name':'model1'}, {'name':'model2'}, {'name':'model3'}, {'name':'model4'}]
    #my_models = [ "model1", "data2", "data3"]
    my_models = json.dumps(my_models)
    my_models = json.loads(my_models)
    if request.method == 'GET':
        if request.GET.get('predict_params'):
            predict_params = request.GET.get('predict_params')
            print predict_params
            request.session['predict_params'] = predict_params

        return render(request, "predict_model.html", {'token': token, 'username': username, 'my_models': my_models})
    if request.method == 'POST':
        predict_params= request.session.get('predict_params', '')
        print predict_params
        data=[]
        for model in request.POST.getlist('checkbox'):
            data.append({"model": model})
        data = json.dumps(data)
        print data

        #return render(request, "task.html", {'token': token, 'username': username})
        return redirect('/task', {'token': token, 'username': username})
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
