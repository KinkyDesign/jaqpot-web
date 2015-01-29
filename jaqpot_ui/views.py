from django.shortcuts import render, redirect
from jaqpot_ui.forms import UserForm
import requests
import subprocess
from django.http import HttpResponseRedirect, HttpResponse

# Create your views here.
def WelcomePage(request):
    return render(request, "mainPage.html")

def Login(request):
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
            url = 'https://opensso.in-silico.ch:443/auth/authenticate?uri=service=openldap'

            token = subprocess.check_output(['curl', '-X', 'POST', '-k', 'https://opensso.in-silico.ch:443/auth/authenticate?uri=service=openldap', '-d', 'username='+username, '-d', 'password='+password])
            if token.startswith("token.id"):
                return redirect('/actions?username='+username+'&token='+token)
                #return render(request, "mainPage.html", {'username': username, 'token': token, 'login': True})
            else:
                error = {"Wrong username or password"}
                return render(request, "login.html", {'form': form, 'error': error})

def CheckUser(request):
     #check if user exists and redirect to mainpage as logged in
     if request.method == 'GET':
         username = request.GET.get('username')
         token = request.GET.get('token')
         print username
         return render(request, "mainPage.html", {'username': username, 'token':token, 'login':True})



