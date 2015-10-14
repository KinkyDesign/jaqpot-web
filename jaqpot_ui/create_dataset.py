__author__ = 'evangelie'

import json
import urllib
from settings import SERVER_URL

def create_dataset( data, username, required_res, img_descriptors):
   #This function creates json dataset

   #replace name with uri
    new_data=[]

    for d in data:
        n_d={}
        n_d1={}
        for key, value in d.items():
            for r in required_res:
                if r['name'] == key:
                    n=r['uri']
                    n_d1[''+n+'']=value
                    n_d.update(n_d1)
        new_data.append(n_d)
    data1 = {}
    data2 = {}
    data3 = {}
    data4 = {}
    data5 = []
    data6 = {}
    data7 = {}
    data8 = {}
    data9 = {}
    data10 = {}
    data11= {}

    data1['comments'] = [""]
    data1['descriptions'] = [""]
    data1['titles'] = ["new dataset"]
    data1['creators'] = [username]
    data1['hasSources'] = [""]
    data2['meta'] = data1

    counter=1
    for d in new_data:
        if img_descriptors:
            if img_descriptors[counter-1]:
                img_descriptors[counter-1] = reformat_key(json.loads(img_descriptors[counter-1]))
                d.update(img_descriptors[counter-1])
        data3["values"] = d
        data4["name"] = 'compound'+str(counter)
        data4["URI"] = 'compound'+str(counter)
        data3["compound"] = data4
        data5.append(data3)
        totalColumns= len(d)
        counter = counter+1
        data3 = {}
        data4 = {}


    data8["dataEntry"]= data5

    data6["descriptors"] = [ "EXPERIMENTAL" ]
    data9["totalColumns"] = totalColumns
    data10["totalRows"] = len(new_data)
    data11["features"] = required_res

    data7.update(data2)
    data7.update(data8)
    data7.update(data6)
    data7.update(data9)
    data7.update(data10)
    data7.update(data11)
    return data7

def chech_image_mopac(model_req):
    image = False
    mopac = False
    for m in model_req:
            if m['category'] == 'IMAGE':
                image = True
            if m['category'] == 'MOPAC':
                mopac = True
    return image, mopac

def reformat_key(d):
    """
    Delete keys with the key ``id`` in a dictionary and chane key format """
    new = {}

    for key, value in d.items():
        if key != "id":
            new_key = SERVER_URL+'/feature/'+urllib.quote_plus('image average particle '+key.encode('utf8') )
            print new_key
            new.update({new_key : value})
    return new
