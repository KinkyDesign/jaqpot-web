from django.shortcuts import redirect, render
import requests
from django.utils.http import urlencode

from jaqpot_ui.settings import SERVER_URL


def token_required(view):
    def _wrapper(request, *args, **kwargs):
        token = request.session.get('token', '')
        if not token:
            return redirect('/login/?next=%s' % request.get_full_path)

        #validate token
        #if token is not valid redirect to login page
        try:
            headers = {
                'Accept': 'application/json',
                'subjectid': token
            }
            r = requests.post(SERVER_URL + '/aa/validate', headers=headers)

            if r.status_code != 200:
                return redirect('/login/?next=%s' % request.get_full_path )
        except Exception as e:
            return render(request, "error.html", {
                'token': token,
                'username': request.session.get('username'),
                'server_error':e,
            })

        return view(request, *args, **kwargs)

    return _wrapper
