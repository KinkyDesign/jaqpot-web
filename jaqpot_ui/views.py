from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
import rdflib
from jaqpot_ui.forms import UserForm, BibtexForm, TrainForm, FeatureForm, ContactForm
import requests
import json
import subprocess
from settings import EXT_AUTH_URL_LOGIN, EXT_AUTH_URL_LOGOUT, URL
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from rdflib import Graph, plugin, term
from rdflib.serializer import Serializer


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
            r = requests.post(EXT_AUTH_URL_LOGIN, data={'username': username, 'password': password})
            if r.status_code == 200: #
                token = r.text.split('=')[1]
                token = token[:-1]

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
        url = EXT_AUTH_URL_LOGOUT + '?subjectid=' + token
        requests.get(url)

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

    all_tasks = []
    #get all tasks with status Running
    headers = {'content-type': 'text/uri-list'}
    res = requests.get(URL+'/tasks?status=Running&creator='+username, headers=headers)
    list_resp = res.text
    list_resp = list_resp.split('\n')[:-1]
    list_run=[]
    for l in list_resp:
        l = l.split('/task/')[1]
        list_run.append({'name': l, 'status': "running"})
        all_tasks.append({'name': l, 'status': "running"})
    list_run = json.dumps(list_run)
    list_run = json.loads(list_run)

    #get all tasks with status Completed
    res = requests.get(URL+'/tasks?status=Completed&creator='+username, headers=headers)
    list_resp = res.text
    list_resp = list_resp.split('\n')[:-1]
    list_complete=[]
    for l in list_resp:
        l = l.split('/task/')[1]
        list_complete.append({'name': l, 'status': "completed"})
        all_tasks.append({'name': l, 'status': "completed"})
    list_complete= json.dumps(list_complete)
    list_complete = json.loads(list_complete)

    #get all tasks with status Cancelled
    res = requests.get(URL+'/tasks?status=Cancelled&creator='+username, headers=headers)
    list_resp = res.text
    list_resp = list_resp.split('\n')[:-1]
    list_cancelled=[]
    for l in list_resp:
        l = l.split('/task/')[1]
        list_cancelled.append({'name': l, 'status': "cancelled"})
        all_tasks.append({'name': l, 'status': "cancelled"})
    list_cancelled= json.dumps(list_cancelled)
    list_cancelled = json.loads(list_cancelled)

    #get all tasks with status Error
    res = requests.get(URL+'/tasks?status=Error&creator='+username, headers=headers)
    list_resp = res.text
    list_resp = list_resp.split('\n')[:-1]
    list_error=[]
    for l in list_resp:
        l = l.split('/task/')[1]
        list_error.append({'name': l, 'status': "error"})
        all_tasks.append({'name': l, 'status': "error"})
    list_error= json.dumps(list_error)
    list_error = json.loads(list_error)


    #get all tasks with status Queued
    res = requests.get(URL+'/tasks?status=Queued&creator='+username, headers=headers)
    list_resp = res.text
    list_resp = list_resp.split('\n')[:-1]
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
        headers = {'content-type': 'text/uri-list'}
        res = requests.get(URL+'/task/'+name, headers=headers)
        g = Graph().parse(URL+'/task/'+name)
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
                output.update({k: o.toPython()})
                print output


        output = json.dumps(output)
        output = json.loads(output)

        return render(request, "taskdetail.html", {'token': token, 'username': username, 'name': name, 'status': status, 'output': output})

#List of all BibTex
def bibtex(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')

    if request.method == 'GET':

        #get all bibtex
        headers = {'content-type': 'text/uri-list'}
        res = requests.get(URL+'/bibtex', headers=headers)
        list_resp = res.text
        list_resp = list_resp.split('\n')[:-1]
        print list_resp
        b=[]
        final_output= []
        #create json with bibtex urls.
        for l in list_resp:
            b.append({"url":l})
            res = requests.get(l, headers=headers)
            list_resp = res.text
            g = Graph().parse(l)

            output = {}
            k=''
            print g

            for s, p, o in g:
                if type(o) == rdflib.term.Literal:
                    if '/bibtex#' in p:
                        k = p.split('/bibtex#')[1]
                        if k=="hasTitle":
                            output.update({k: o.toPython()})
                        if k=="hasAuthor":
                            output.update({k: o.toPython()})
            id = l.split('/bibtex/')[1]
            output.update({"id" : id})
            final_output.append(output)

        #get json data
        final_output = json.dumps(final_output)
        final_output = json.loads(final_output)

        '''list_run=[]
        for l in list_resp:
            l = l.split('/task/')[1]
            list_run.append({'name': l, 'status': "running"})
            all_tasks.append({'name': l, 'status': "running"})
        list_run = json.dumps(list_run)
        list_run = json.loads(list_run) '''


        return render(request, "bibtex.html", {'token': token, 'username': username, 'name': name, 'final_output': final_output})

#Details of each bibtex
def bib_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    id = request.GET.get('id')
    #send request
    headers = {'content-type': 'text/uri-list'}
    res = requests.get(URL+'/bibtex/'+id, headers=headers)
    list_resp = res.text
    #get rdf response and convert to json data with details for bibtex
    g = Graph().parse(URL+'/bibtex/'+id)
    details = {}
    k=''
    print g

    for s, p, o in g:
        if type(o) == rdflib.term.Literal:
            if '/bibtex#' in p:
                k = p.split('/bibtex#')[1]
                if k=="hasTitle":
                    details.update({"Title": o.toPython()})
                if k=="hasAuthor":
                    details.update({"author": o.toPython()})
                if k=="hasKeywords":
                    details.update({"Keywords": o.toPython()})
                if k=="hasVolume":
                    details.update({"Volume": o.toPython()})
                if k=="hasCopyright":
                    details.update({"Copyright": o.toPython()})
                if k=="hasJournal":
                    details.update({"Journal": o.toPython()})
                if k=="hasAbstract":
                    details.update({"Abstract": o.toPython()})
                if k=="hasPages":
                    details.update({"Pages": o.toPython()})
                if k=="hasAddress":
                    details.update({"Address": o.toPython()})
                if k=="hasYear":
                    details.update({"Year": o.toPython()})
                if k=="hasURL":
                    details.update({"Url": o.toPython()})

    #get json data
    details = json.dumps(details)
    details = json.loads(details)
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
        #headers = {'content-type': 'text/uri-list'}
        #r = requests.get('http://opentox.informatik.tu-muenchen.de:8080/OpenTox-dev/model', headers=headers)
        #print r.text
        contacts = {'name': username, 'maxtasks': 5, 'maxmodels': 2000, 'maxalgorithms': 2000, 'models': 100, 'tasks':2, 'alg': 1000}
        contacts = json.dumps(contacts)

        return render(request, "user_details.html", {'token': token, 'username': username, 'name': name, 'contacts': contacts})

def trainmodel(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    form = TrainForm(initial={})

    if request.method == 'GET':
        entries = [ "svm", "mlr", "alg_3"]
        entries_2 = [ "a1", "a2", "a3"]
        entries_3 = [ "1", "2", "3"]
        return render(request, "train_model.html", {'token': token, 'username': username, 'entries': entries, 'entries_2': entries_2, 'entries_3': entries_3, 'form':form})

    if request.method == 'POST':
        data=[]
        for alg in request.POST.getlist('checkbox'):
            data.append({"alg":alg})
        data = json.dumps(data)
        #data = json.loads(data)
        #get algorithm to the session
        request.session['algorithm'] = data
        #return redirect('/dataset?data='+data, {'data': data})
        entries = [ "data", "data2", "data3"]
        entries2 = [ "data", "data2", "data3"]
        return render(request, "choose_dataset.html", {'token': token, 'username': username, 'entries': entries, 'entries2': entries2, 'data':data})

'''def choose_dataset(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.method == 'GET':
        data = request.GET.get('data')
        print data
        entries = [ "data", "data2", "data3"]
        entries2 = [ "data", "data2", "data3"]
        return render(request, "choose_dataset.html", {'token': token, 'username': username, 'entries': entries, 'entries2': entries2, 'data':data})'''

def alg(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')


    if request.method == 'GET':

        alg = request.session.get('algorithm', '')
        dataset = request.GET.get('dataset')
        #alg = json.loads(alg)
        #for a in alg:
            #r = request.get() get algorithm parameters
            #r.append('{ r}')
        #alg_param = [{'alg':'svm ', 'kernel': 'rdf', 'gamma':0.5, 'e':0.1},{'alg':'svm ', 'kernel': 'rdf', 'gamma':0.5, 'e':0.1}]
        alg_param = [{'alg':'svm ', 'kernel': 'rdf', 'gamma': 0.5, 'e': 0.1}]
        print alg
        print dataset
        return render(request, "alg.html", {'token': token, 'username': username, 'alg':alg, 'dataset':dataset, 'alg_param': alg_param})

#Conformer
def conformer(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.method == 'GET':
        return render(request, "conformer.html", {'token': token, 'username': username})
    if request.method == 'POST':
        #add task for descriptors calculation
        return render(request, "task.html", {'token': token, 'username': username})

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
    if request.method == 'GET':
        dataset= [{'name':'dataset1'}, {'name':'dataset2'}, {'name':'dataset3'}, {'name':'dataset4'}]
        return render(request, "dataset.html", {'token': token, 'username': username, 'dataset': dataset})

def dataset_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name', '')
    if request.method == 'GET':
        return render(request, "dataset_detail.html", {'token': token, 'username': username, 'name': name})

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

        return render(request, "task.html", {'token': token, 'username': username})

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

            recipients = ['evangelie_5@hotmail.com']
            #css the sender mail
            recipients.append(sender)
            send_mail(subject, message, sender, recipients)
            return HttpResponseRedirect('/thanks/') # Redirect after POST
        else:
            error = "Invalid value"
            return render_to_response('contact_form.html', {'form': form, 'token': token, 'username': username, 'error': error}, context_instance=RequestContext(request))
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

