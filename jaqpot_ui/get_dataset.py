from django.shortcuts import render, redirect

__author__ = 'evangelie'

import json
import requests
from settings import SERVER_URL


def paginate_dataset(request, name, token, username, page):
    '''
    :param request: request
    :param name: name of dataset
    :param token: user token
    :param username: username
    :param page: page of dataset
    :return: data_detail, last, page

    This function returns the compounds of the selected dataset paginated
    '''
    headers = {'Accept': 'application/json', 'subjectid': token}
    try:
        r = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart=0&rowMax=0&colStart=0&colMax=0', headers=headers)
    except Exception as e:
        return render(request, "error.html", {'token': token, 'username': username,'server_error':e, })
    if r.status_code >= 400:
        return render(request, "error.html", {'token': token, 'username': username,'error': json.loads(r.text)})
    data=json.loads(r.text)
    if str(r) != "<Response [200]>":
        #redirect to error page
        return render(request, "error.html", {'token': token, 'username': username,'error':data})
    else:
        totalRows = data['totalRows']
        totalColumns = data['totalColumns']
        last = (totalRows/20)
        if (totalRows%20) != 0:
            last=last+1
        if last==0:
            last=1
        if request.method == 'GET':
            headers = {'Accept': 'application/json', 'subjectid': token}
            #print data_detail['dataEntry']
            if page:
                page1=int(page) * 20 - 20
                k=str(page1)
                if page1 <= 1:
                    if totalRows>20:
                        res = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart=0&rowMax=20&colStart=0&colMax='+str(totalColumns), headers=headers)
                        data_detail= json.loads(res.text)
                    else:
                        res = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart=0&rowMax='+str(totalRows-int(k))+'&colStart=0&colMax='+str(totalColumns), headers=headers)
                        data_detail= json.loads(res.text)
                else:
                    if totalRows>int(k)+20:
                        res = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart='+k+'&rowMax=20&colStart=0&colMax='+str(totalColumns), headers=headers)
                        data_detail = json.loads(res.text)
                    else:
                        res = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart='+k+'&rowMax='+str(totalRows-int(k))+'&colStart=0&colMax='+str(totalColumns), headers=headers)
                        data_detail = json.loads(res.text)
            else:
                page = 1
                if totalRows>20:
                    res = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart=0&rowMax=20&colStart=0&colMax='+str(totalColumns), headers=headers)
                else:
                    res = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart=0&rowMax='+str(totalRows)+'&colStart=0&colMax='+str(totalColumns), headers=headers)

            data_detail=json.loads(res.text)
            return data_detail, last, page


def get_prediction_feature_of_dataset(dataset, token):
    headers = {'Accept': 'application/json', 'subjectid': token}
    r = requests.get(SERVER_URL+'/dataset/'+dataset, headers=headers)
    data=json.loads(r.text)
    prediction_feature = ""
    for d in data['dataEntry']:
        values =  d['values']
        for k,v in values.items():
            if v == None:
                prediction_feature = k
                break
        if prediction_feature != "":
            break
    return prediction_feature

def get_prediction_feature_name_of_dataset(dataset, token, prediction):
    headers = {'Accept': 'application/json', 'subjectid': token}
    r = requests.get(SERVER_URL+'/dataset/'+dataset, headers=headers)
    data=json.loads(r.text)
    for f in data['features']:
        if f['uri'] == prediction:
            name = f['name']
            break
    return name

def get_number_of_not_null_of_dataset(dataset, token, prediction_feature):
    headers = {'Accept': 'application/json', 'subjectid': token}
    r = requests.get(SERVER_URL+'/dataset/'+dataset, headers=headers)
    data=json.loads(r.text)
    total = 0
    for d in data['dataEntry']:
        values =  d['values']
        for k,v in values.items():
            if k  == prediction_feature:
                if v != None:
                    total = total+1
    return total