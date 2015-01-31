from django.shortcuts import render, redirect
from jaqpot_ui.forms import UserForm
import requests
import json
import subprocess
from settings import EXT_AUTH_URL_LOGIN, EXT_AUTH_URL_LOGOUT
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

