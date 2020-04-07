from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ContactForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your name",
                "id": "form_name"
            }
            )
        )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "How can we reach you",
                "id": "form_email"
            }
            ))

    content = forms.CharField(
            widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Anything you wanna tell us",
                "id": "form_content"
            }
            )
        )

    # def clean_email(self):
    #     email = self.cleaned_data.get("email")
    #     if not "gmail.com" in email:
    #         raise forms.ValidationError("Email has to be gmail.com")
    #     return email


