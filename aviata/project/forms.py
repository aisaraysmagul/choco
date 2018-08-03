from django import forms
from django.forms.widgets import SelectDateWidget

class PostForm (forms.Form):
    # id = forms.IntegerField()
    start_date = forms.DateField(widget=SelectDateWidget)
    end_date = forms.DateField(widget=SelectDateWidget)
    CHOICES = (('Kaspi', 'Kaspi'), ('Processing', 'Processing'), ('Tourism', 'Tourism'), ('Kazkom', 'Kazkom'))
    name = forms.ChoiceField(choices=CHOICES)



class UpdateForm(forms.Form):
    id = forms.IntegerField()
