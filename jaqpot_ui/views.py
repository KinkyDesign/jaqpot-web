from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
import rdflib
from jaqpot_ui.forms import UserForm, BibtexForm, TrainForm, FeatureForm, ContactForm
import requests
import json
import subprocess
from settings import EXT_AUTH_URL_LOGIN, EXT_AUTH_URL_LOGOUT, URL, EMAIL_HOST_USER, URL_1
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from rdflib import Graph, plugin, term
from rdflib.serializer import Serializer
from jaqpot_ui.templatetags import templates_extras


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
            else:
                error = "Wrong username or password"
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

#List of all tasks
def task(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if token:
        request.session.get('token', '')
    #validate token
    #if token is not valid redirect to login page

    #else go to tasks
    all_tasks = []
    #get all tasks with status Running
    headers = {'Accept': 'text/uri-list', 'subjectid': token}
    res = requests.get(URL_1+'/task?creator='+username+'&status=RUNNING', headers=headers)
    list_resp = res.text
    list_resp = list_resp.splitlines()
    list_run=[]
    for l in list_resp:
        l = l.split('/task/')[1]
        list_run.append({'name': l, 'status': "running"})
        all_tasks.append({'name': l, 'status': "running"})
    list_run = json.dumps(list_run)
    list_run = json.loads(list_run)

    #get all tasks with status Completed
    res = requests.get(URL_1+'/task?status=COMPLETED&creator='+username, headers=headers)
    list_resp = res.text
    list_resp = list_resp.splitlines()
    list_complete=[]
    for l in list_resp:
        l = l.split('/task/')[1]
        list_complete.append({'name': l, 'status': "completed"})
        all_tasks.append({'name': l, 'status': "completed"})
    list_complete= json.dumps(list_complete)
    list_complete = json.loads(list_complete)

    #get all tasks with status Cancelled
    res = requests.get(URL_1+'/task?status=CANCELLED&creator='+username, headers=headers)
    list_resp = res.text
    list_resp = list_resp.splitlines()
    list_cancelled=[]
    for l in list_resp:
        l = l.split('/task/')[1]
        list_cancelled.append({'name': l, 'status': "cancelled"})
        all_tasks.append({'name': l, 'status': "cancelled"})
    list_cancelled= json.dumps(list_cancelled)
    list_cancelled = json.loads(list_cancelled)

    #get all tasks with status Error
    res = requests.get(URL_1+'/task?status=ERROR&creator='+username, headers=headers)
    list_resp = res.text
    list_resp = list_resp.splitlines()
    list_error=[]
    for l in list_resp:
        l = l.split('/task/')[1]
        list_error.append({'name': l, 'status': "error"})
        all_tasks.append({'name': l, 'status': "error"})
    list_error= json.dumps(list_error)
    list_error = json.loads(list_error)


    #get all tasks with status Queued
    res = requests.get(URL_1+'/task?status=QUEUED&creator='+username, headers=headers)
    list_resp = res.text
    list_resp = list_resp.splitlines()
    list_queued=[]
    for l in list_resp:
        l = l.split('/task/')[1]
        list_queued.append({'name': l, 'status': "queued"})
        all_tasks.append({'name': l, 'status': "queued"})
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

    if request.method == 'GET':
        #get task details in rdf format
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(URL_1+'/task/'+name, headers=headers)
        print res.text
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

        return render(request, "taskdetail.html", {'token': token, 'username': username, 'name': name, 'status': status, 'output': output})

#stop running task
def stop_task(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    if request.method == 'GET':
        #stop task
        headers = {'content-type': 'text/uri-list'}
        res = requests.delete(URL+'/task/'+name, headers=headers)
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
        res = requests.get(URL_1+'/bibtex?bibtype=Entry&creator='+username, headers=headers1)
        list_resp = res.text
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
    #send request
    headers = {'Accept': 'application/json', 'subjectid': token}
    res = requests.get(URL_1+'/bibtex/'+id, headers=headers)
    list_resp = res.text
    #get json data
    details = json.loads(res.text)
    print details
    if request.method == 'GET':

        return render(request, "bibdetail.html", {'token': token, 'username': username, 'name': name, 'details': details })

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

        json_b= {'author': form['author'].value(), 'abstract': form['abstract'].value(), 'title': form['title'].value(),
                 'copyright': form['copyright'].value(),'address':form['address'].value(), 'year': form['year'].value(),
                 'pages':form['pages'].value(), 'volume':form['volume'].value(), 'journal': form['journal'].value(),
                 'keyword':form['keyword'].value(), 'url':form['url'].value()}
        bibtex_entry = json.dumps(json_b)
        print bibtex_entry
        #it should send request with the new entry for saving
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

    if request.method == 'GET':
        entries = [ "data", "data2", "data3"]
        entries2 = [ "data", "data2", "data3"]
        return render(request, "choose_dataset.html", {'token': token, 'username': username, 'entries': entries, 'entries2': entries2})


def choose_dataset(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    form = TrainForm(initial={})
    if request.method == 'GET':
        dataset = request.GET.get('dataset')
        entries = [ "svm", "mlr", "alg_3"]
        entries_2 = [ "a1", "a2", "a3"]
        entries_3 = [ "1", "2", "3"]
        return render(request, "train_model.html", {'token': token, 'username': username, 'entries': entries, 'entries_2': entries_2, 'entries_3': entries_3, 'form':form, 'dataset': dataset})
    if request.method == 'POST':
        algorithms=[]
        for alg in request.POST.getlist('checkbox'):
            algorithms.append({"alg":alg})
        algorithms = json.dumps(algorithms)
        print algorithms
        dataset = request.GET.get('dataset')
        #alg_param = [{'alg':'svm ', 'kernel': 'rdf', 'gamma':0.5, 'e':0.1},{'alg':'svm ', 'kernel': 'rdf', 'gamma':0.5, 'e':0.1}]
        alg_param = [{'alg':'svm ', 'kernel': 'rdf', 'gamma': 0.5, 'e': 0.1}]
        print dataset
        return render(request, "alg.html", {'token': token, 'username': username, 'dataset':dataset, 'alg_param': alg_param})

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
    if request.method == 'GET':
        #get all models
        #headers = {'Accept:text/uri-list'}
        #r = requests.get('http://opentox.informatik.tu-muenchen.de:8080/OpenTox-dev/model', headers=headers)
        #print r.text
        models = []
        #get all models
        headers = {'content-type': 'text/uri-list'}
        res = requests.get(URL+'/model', headers=headers)
        list_resp = res.text
        list_resp = list_resp.split('\n')[:-1]
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
    details = [{'a':'0.1','b':'0.2', 'description':'model'}]
    #get task details in rdf format
    headers = {'content-type': 'text/uri-list'}
    res = requests.get(URL+'/model/'+name, headers=headers)
    #print res.text


    if request.method == 'GET':
        return render(request, "model_detail.html", {'token': token, 'username': username, 'details':details, 'name':name })

def features(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

    if request.method == 'GET':
        features = [{ 'name':'feature1'}, {'name':'feature2'}, {'name':'feature3'},{'name':'feature4' }]
        return render(request, "features.html", {'token': token, 'username': username, 'features': features})
def feature_details(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')

    if request.method == 'GET':
        return render(request, "feature_details.html", {'token': token, 'username': username, 'name': name})

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

def algorithm(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')

    if request.method == 'GET':
         algorithms = []
         #get all algorithms
         headers = {'Accept': 'text/uri-list'}
         res = requests.get(URL+'/algorithm', headers=headers)
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
        headers = {'content-type': 'text/uri-list'}
        res = requests.get(URL+'/algorithm/'+algorithm, headers=headers)
        #get rdf response and convert to json data with details for bibtex
        g = Graph().parse(URL+'/algorithm/'+algorithm)
        details = {}
        sub= []
        i=1
        j=1
        t=1
        k=''
        for s, p, o in g:
            if type(o) == rdflib.term.Literal:
                if 'algorithm/'+algorithm in s:

                    if 'elements/1.1/' in p:
                        k = p.split('elements/1.1/')[1]
                        '''if k == 'subject':
                            sub.append(o.toPython())
                            i=i+1
                            details.update(sub)
                            details.update({'num_of_sub': i-1})'''
                        '''if k == 'contributor':
                            sub.update({"contributor"+str(j): o.toPython()})
                            j=j+1
                            details.update(sub)
                            details.update({'num_of_cont': j-1})
                        if k == 'title':
                            sub.update({"title"+str(t): o.toPython()})
                            t=t+1
                            details.update(sub)
                            details.update({'num_of_cont': t-1})'''


                        details.update({k: o.toPython()})

        #details.update({'subject': sub})
        details = json.dumps(details)
        details = json.loads(details)
        return render(request, "algorithm_detail.html", {'token': token, 'username': username, 'details': details})

def dataset(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    dataset=[]
    if request.method == 'GET':
        headers = {'Accept': 'text/uri-list', "subjectid": token}
        res = requests.get(URL_1+'/dataset', headers=headers)
        data= res.text
        data = data.splitlines()
        for l in data:
            l = l.split('/dataset/')[1]
            dataset.append({'name': l})
        return render(request, "dataset.html", {'token': token, 'username': username, 'dataset': dataset})

def dataset_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name', '')
    if request.method == 'GET':
        headers = {'Accept': 'application/json', 'subjectid': token}
        res = requests.get(URL_1+'/dataset/'+name, headers=headers)
        data_detail=json.loads(res.text)
        print data_detail
        return render(request, "dataset_detail.html", {'token': token, 'username': username, 'name': name, 'data_detail': data_detail})

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
