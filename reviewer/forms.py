from django import forms

class ReviewForm(forms.Form):
    text = forms.CharField(label='Write your own review:', max_length=1000)
