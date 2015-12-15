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
    #title = forms.CharField(max_length=50)
    file = forms.FileField(error_messages={'required': 'Please choose a file.'})
    feature = forms.ChoiceField(widget = forms.Select(), choices=[])

class SelectPmmlForm(forms.Form):
    predicted_feature = forms.ChoiceField(widget = forms.Select(), choices=[])
    pmml = forms.ChoiceField(widget = forms.Select(), choices=[])

class InputForm(forms.Form):
    input = forms.MultipleChoiceField(error_messages={'required': 'Please select input.'}, widget = forms.CheckboxSelectMultiple(), choices=[], required=True)
    input.widget.attrs.update({'class' : "input"})
    output = forms.ChoiceField(error_messages={'required': 'Please select output.'}, widget = forms.RadioSelect(), choices=[], required= True)
class NoPmmlForm(forms.Form):
    pred_feature = forms.ChoiceField(widget = forms.Select(), choices=[])

class TrainingForm(forms.Form):
    scaling = forms.ChoiceField(widget = forms.Select(), choices=[( 'scaling1', 'None' ), ('scaling2', 'Scaling between zero and one'), ('scaling3', 'Normalization')])
    doa = forms.ChoiceField(widget = forms.Select(), choices=[( 'doa1', 'None' ), ('doa2', 'Leverage method'), ('doa3', 'Other method')])
    modelname = forms.CharField(max_length=50, required= True)
    description = forms.CharField(widget=forms.Textarea, required= True)
    description.widget.attrs.update({'style' : "border-radius: 4px;"})
    variables = forms.ChoiceField(error_messages={'required': 'Please select variables.'}, widget = forms.RadioSelect(), choices=[( 'input', 'Select Input variable and endpoint' ), ('pm', 'Select PMML'), ('file', 'Upload PMML file'), ('none', 'None')])


class DatasetForm(forms.Form):
    title = forms.CharField(max_length=50, required= True)
    description = forms.CharField(widget=forms.Textarea, required= True)

class ValidationForm(forms.Form):
    pred_feature = forms.ChoiceField(widget = forms.Select(), choices=[])
    folds = forms.ChoiceField(widget = forms.Select(), choices=[( '3', '3'), ('5', '5'), ('10', '10')])
    stratify = forms.ChoiceField(widget = forms.Select(), choices=[( ' ', 'None'), ('1', '1'), ('2', '2')])

class ExperimentalParamsForm(forms.Form):
    levels = forms.CharField(required=True, error_messages={'required': 'Please enter levels.'},  widget=forms.TextInput(attrs={'style': "margin:5px;"}))
    nVars = forms.CharField(required=True, error_messages={'required': 'Please enter nVars.'}, widget=forms.TextInput(attrs={'style': "margin:5px;"}))
    factors = forms.CharField(required=True, error_messages={'required': 'Please enter factors.'}, widget=forms.TextInput(attrs={'style': "margin:5px;"}))
    varNames = forms.CharField(required=True, error_messages={'required': 'Please enter varNames.'}, widget=forms.TextInput(attrs={'style': "margin:5px;"}))
    nTrials = forms.CharField(required=True, error_messages={'required': 'Please enter nTrials.'}, widget=forms.TextInput(attrs={'style': "margin:5px;"}))
    criterion = forms.CharField(required=True, error_messages={'required': 'Please enter criterion.'}, widget=forms.TextInput(attrs={'style': "margin:5px;"}))
    form = forms.CharField(required=True, error_messages={'required': 'Please enter form.'}, widget=forms.TextInput(attrs={'style': "margin:5px;"}))