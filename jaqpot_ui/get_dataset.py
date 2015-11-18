from django.shortcuts import render

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
    r = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart=0&rowMax=0&colStart=0&colMax=0', headers=headers)
    data=json.loads(r.text)
    if str(r) != "<Response [200]>":
        #redirect to error page
        return render(request, "error.html", {'token': token, 'username': username,'error':data})
    else:
        totalRows = data['totalRows']
        totalColumns = data['totalColumns']
        last = (totalRows/20)
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
                        res = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart=0&rowMax='+str(totalRows)+'&colStart=0&colMax='+str(totalColumns), headers=headers)
                        data_detail= json.loads(res.text)
                else:
                    if totalRows>int(k)+20:
                        res = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart='+k+'&rowMax=10&colStart=0&colMax='+str(totalColumns), headers=headers)
                        data_detail = json.loads(res.text)
                    else:
                        res = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart='+k+'&rowMax='+str(totalRows)+'&colStart=0&colMax='+str(totalColumns), headers=headers)
                        data_detail = json.loads(res.text)
            else:
                page = 1
                if totalRows>20:
                    res = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart=0&rowMax=20&colStart=0&colMax='+str(totalColumns), headers=headers)
                else:
                    res = requests.get(SERVER_URL+'/dataset/'+name+'?rowStart=0&rowMax='+str(totalRows)+'&colStart=0&colMax='+str(totalColumns), headers=headers)
            data_detail=json.loads(res.text)
            return data_detail, last, page