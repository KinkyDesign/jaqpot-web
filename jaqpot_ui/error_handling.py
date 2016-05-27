from django.shortcuts import render
import json


def error_handling(request, res, token, username):
    if res.status_code >= 400:
            #redirect to error page
            return render(request, "error.html", {'token': token, 'username': username,'error':json.loads(res.text)})
