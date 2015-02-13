from django.shortcuts import render, redirect
from jaqpot_ui.forms import UserForm, BibtexForm, TrainForm
import requests
import json
import subprocess
from settings import EXT_AUTH_URL_LOGIN, EXT_AUTH_URL_LOGOUT
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse


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
    #r = requests.get('http://opentox.informatik.tu-muenchen.de:8080/OpenTox-dev/task')
    #print r.text
    list = [{'name': "task1", 'status':"running"}, {'name': "task2", 'status':"completed"}, {'name': "task3", 'status':"cancelled"}]
    list = json.dumps(list)
    list = json.loads(list)
    if request.method == 'GET':
        return render(request, "task.html", {'list': list, 'token': token, 'username': username})

#More information about each task
def taskdetail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    status = request.GET.get('status')

    if request.method == 'GET':
        task_info = {"id": "12", "ETA": 2, "percentage": 40}
        task_info = json.dumps(task_info)
        return render(request, "taskdetail.html", {'token': token, 'username': username, 'name': name, 'task_info': task_info, 'status':status})

#List of all BibTex
def bibtex(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')

    if request.method == 'GET':
        #create json data
        list_of_bibtex = [
            {'id':1, 'author':'Sarimveis H., Alexandridis A., Bafas G.', 'information':'A fast training algorithm for RBF networks based on subtractive clustering'},
            {'id':2, 'author':'Sarimveis H., Alexandridis A., Bafas G.', 'information':'A fast training algorithm for RBF networks based on subtractive clustering'},
            {'id':3, 'author':'Sarimveis H., Alexandridis A., Bafas G.', 'information':'A fast training algorithm for RBF networks based on subtractive clustering'},
            {'id':4, 'author':'Sarimveis H., Alexandridis A., Bafas G.', 'information':'A fast training algorithm for RBF networks based on subtractive clustering'},
            {'id':5, 'author':'Sarimveis H., Alexandridis A., Bafas G', 'information':'A fast training algorithm for RBF networks based on subtractive clustering'},
            {'id':6, 'author':'Sarimveis H., Alexandridis A., Bafas G', 'information':'A fast training algorithm for RBF networks based on subtractive clustering'},
            {'id':7, 'author':'Sarimveis H., Alexandridis A., Bafas G', 'information':'A fast training algorithm for RBF networks based on subtractive clustering'},
            {'id':8, 'author':'Sarimveis H., Alexandridis A., Bafas G', 'information':'A fast training algorithm for RBF networks based on subtractive clustering'},
            {'id':9, 'author':'Sarimveis H., Alexandridis A., Bafas G', 'information':'A fast training algorithm for RBF networks based on subtractive clustering'},
        ]
        #get json data
        list_of_bibtex = json.dumps(list_of_bibtex)
        list_of_bibtex = json.loads(list_of_bibtex)
        paginator = Paginator(list_of_bibtex, 25) # Show 25 contacts per page

        page = request.GET.get('page')
        try:
            list_of_bibtex = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            list_of_bibtex = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            list_of_bibtex = paginator.page(paginator.num_pages)

        return render(request, "bibtex.html", {'token': token, 'username': username, 'name': name, 'list_of_bibtex' : list_of_bibtex})

#Details of each bibtex
def bib_detail(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    name = request.GET.get('name')
    details = { 'author':'Sarimveis H., Alexandridis A., Bafas G.',
                'Abstract' : 'A new algorithm for training radial basis function neural networks is presented in this paper. The algorithm, which is based on the subtractive clustering technique, has a number of advantages compared to the traditional learning algorithms, including faster training times and more accurate predictions. Due to these advantages the method proves suitable for developing models for complex nonlinear systems.',
                'Title' : "A fast training algorithm for RBF networks based on subtractive clustering",
                'Copyright' : "Copyright 2003 Elsevier Science B.V. All rights reserved.",
                'Address' : "National Technical University of Athens, School of Chemical Engineering, 9 Heroon Polytechniou str., Zografou Campus, Athens 15780, Greece",
                'Year' : "2003",
                'Pages' : "501-505",
                'Volume' : "51",
                'Journal' : "Neurocomputing",
                'Keywords' : "Radial basis function networks, Training algorithms, Model selection",
                'Url' : "http://dx.doi.org/10.1016/S0925-2312(03)00342-4",
                'text': 'sdxcfvgbhnjmk,l',

                }
    #get json data
    details = json.dumps(details)
    details = json.loads(details)
    if request.method == 'GET':

        return render(request, "bibdetail.html", {'token': token, 'username': username, 'name': name, 'details': details})

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
                 'keyword':form['keyword'].value(), 'url':form['url'].value() }
        bibtex_entry = json.dumps(json_b)
        print bibtex_entry
        #it should send request with the new entry for saving
        return render(request, "mainpage.html", {'token': token, 'username': username, 'name': name})

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
        contacts = {'name': "guest", 'maxtasks': 5, 'maxmodels': 2000, 'maxalgorithms': 2000, 'models': 100, 'tasks':2, 'alg': 1000}
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
            data.append({"alg": alg})
        data = json.dumps(data)
        return redirect('/dataset?data='+data, {'data': data})

def choose_dataset(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.method == 'GET':
        data = request.GET.get('data')
        print data
        entries = [ "data", "data2", "data3"]
        entries2 = [ "data", "data2", "data3"]
        return render(request, "choose_dataset.html", {'token': token, 'username': username, 'entries': entries, 'entries2': entries2, 'data':data})

def alg(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.method == 'GET':
        alg = request.GET.get('alg')
        dataset = request.GET.get('dataset')
        alg = json.loads(alg)
        #for a in alg:
            #r = request.get() get algorithm parameters
            #r.append('{ r}')
        alg_param = [{'alg':'svm ', 'kernel': 'rdf', 'gamma':0.5, 'e':0.1},{'alg':'svm ', 'kernel': 'rdf', 'gamma':0.5, 'e':0.1}]
        print alg
        print dataset
        return render(request, "alg.html", {'token': token, 'username': username, 'alg':alg, 'dataset':dataset, 'alg_param': alg_param})

#Conformer
def conformer(request):
    token = request.session.get('token', '')
    username = request.session.get('username', '')
    if request.method == 'GET':
        return render(request, "conformer.html", {'token': token, 'username': username})