from django import forms

class ReviewForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control bg-dark', 'aria-label':'With textarea', 'style':'height:100px'}), label='', max_length=1000)
