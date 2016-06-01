__author__ = 'evangelie'
import json

def get_params(request, parameters, al):
    params={}
    for p in parameters:
        print p
        try:
            value = int(request.POST.get(''+p))
            params.update({str(p):[value]})
        except:
            try:
                value = float(request.POST.get(''+p))
                params.update({str(p):[value]})
            except:
                value = request.POST.get(''+p)
                v = value.split(',')
                params.update({str(p):v})

        for a in al['parameters']:
            if (a['name'] == p):
                if type(a['value']== "list"):
                    a['value']=[request.POST.get(''+p)]
                elif type(a['value']== "unicode"):
                    a['value']=request.POST.get(''+p)
    return params, al

def get_params2(request, parameters, al):
    params={}
    for p in parameters:
        try:
            value = int(request.POST.get(''+p))
            params.update({str(p):[value]})
        except:
            value = request.POST.get(''+p)
            v = value.split(',')
            print v
            params.update({str(p):json.dumps(v)})

        for a in al['parameters']:
            if (a['name'] == p):
                a['value']=[request.POST.get(''+p)]
    return params, al

def get_params3(request, parameters, al):
    params={}
    for p in parameters:
        try:
            value = int(request.POST.get(''+p))
            params.update({p:value})
        except:
            try:
                value = float(request.POST.get(''+p))
                params.update({p:value})
            except:
                value = request.POST.get(''+p)
                params.update({p:value})

        for a in al['parameters']:
            if (a['name'] == p):
                a['value']=[request.POST.get(''+p)]
    return params, al

def get_params4(request, parameters, al):
    params={}
    for p in parameters:
        try:
            value = int(request.POST.get(''+p))
            params.update({p:value})
        except:
            try:
                value = float(request.POST.get(''+p))
                params.update({p:value})
            except:
                value = request.POST.get(''+p)
                params.update({p:value})

        for a in al['parameters']:
            if (a['name'] == p):
                a['value']=request.POST.get(''+p)
    return params, al