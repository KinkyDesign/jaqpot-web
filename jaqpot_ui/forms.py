from django import forms
from captcha.fields import CaptchaField

class UserForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput())
MY_CHOICES = (
    ('Article', 'Article'),
    ('Entry', 'Entry'),
    ('Conference', 'Conference'),
)

class BibtexForm(forms.Form):
        author = forms.CharField(error_messages={'required': 'Please enter author.'})
        abstract = forms.CharField(error_messages={'required': 'Please enter abstract.'})
        title = forms.CharField(error_messages={'required': 'Please enter title.'})
        copyright = forms.CharField(error_messages={'required': 'Please enter copyright.'})
        address = forms.CharField(error_messages={'required': 'Please enter address.'})
        year = forms.CharField(error_messages={'required': 'Please enter year.'})
        pages = forms.CharField(error_messages={'required': 'Please enter number of pages.'})
        volume = forms.CharField( error_messages={'required': 'Please enter volume.'})
        journal = forms.CharField(error_messages={'required': 'Please enter journal.'})
        keyword = forms.CharField(error_messages={'required': 'Please enter keyword.'})
        url = forms.URLField(error_messages={'required': 'Please enter url.'})
        type = forms.ChoiceField(choices=MY_CHOICES)

class FeatureForm(forms.Form):
        feature = forms.CharField()

class TrainForm(forms.Form):
         alg = forms.CharField()

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100, error_messages={'required': 'Please enter subject.'}, widget=forms.TextInput(attrs={'placeholder':'Subject'}))
    sender = forms.EmailField(error_messages={'required': 'Please enter your mail'},widget=forms.EmailInput(attrs={'placeholder':'Email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'rows':'3'}), error_messages={'required': 'Please enter your message'})
    captcha = CaptchaField()

class SubstanceownerForm(forms.Form):
        substanceowner = forms.CharField()

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
    feature = forms.ChoiceField(widget = forms.Select(), choices=[])

class SelectPmmlForm(forms.Form):
    feature = forms.ChoiceField(widget = forms.Select(), choices=[])
    pmml = forms.ChoiceField(widget = forms.Select(), choices=[])

class InputForm(forms.Form):
    input = forms.ChoiceField(widget = forms.CheckboxSelectMultiple(), choices=[], required=True)
    output = forms.ChoiceField(widget = forms.RadioSelect(), choices=[], required= True)

class NoPmmlForm(forms.Form):
    feature = forms.ChoiceField(widget = forms.Select(), choices=[])

class TrainingForm(forms.Form):
    scaling = forms.ChoiceField(widget = forms.Select(), choices=[( 'scaling1', 'None' ), ('scaling2', 'Scaling between zero and one'), ('scaling3', 'Normalization')])
    doa = forms.ChoiceField(widget = forms.Select(), choices=[( 'doa1', 'None' ), ('doa2', 'Leverage method'), ('doa3', 'Other method')])
    modelname = forms.CharField(max_length=50, required= False)
    description = forms.CharField(max_length=200, required= False)
    variables = forms.ChoiceField(widget = forms.RadioSelect(), choices=[( 'input', 'Select Input variable and endpoint' ), ('pm', 'Select PMML'), ('file', 'Upload PMML file'), ('none', 'None')])