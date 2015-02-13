from django import forms

class UserForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput())

class BibtexForm(forms.Form):
        author = forms.CharField()
        abstract = forms.CharField()
        title = forms.CharField()
        copyright = forms.CharField()
        address = forms.CharField()
        year = forms.CharField()
        pages = forms.CharField()
        volume = forms.CharField()
        journal = forms.CharField()
        keyword = forms.CharField()
        url = forms.CharField()
class TrainForm(forms.Form):
         alg = forms.CharField()