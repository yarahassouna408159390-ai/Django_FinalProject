from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    stars = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={"class":"form-select"})
    )

    class Meta:
        model = Review
        fields = ['stars', 'comment']
        widgets = {
            "comment": forms.Textarea(attrs={"class":"form-control", "rows": 4}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={"class":"form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class":"form-control"}))
    subject = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class":"form-control"}))
    message = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control", "rows": 5}))
