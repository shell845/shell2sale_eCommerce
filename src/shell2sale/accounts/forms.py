from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import EmailActivation, GuestEmail
from .signals import user_logged_in


User = get_user_model()


class ReactivateEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            register_link = reverse("register")
            msg = """This email does not exist, would you like to <a href="{link}">register</a>?
                    """.format(link=register_link)
            raise forms.ValidationError(mark_safe(msg))
        return email


class UserDetailChangeForm(forms.ModelForm):
    full_name = forms.CharField(label='Name', required=False, widget=forms.TextInput(attrs={"class": 'form-control'}))

    class Meta:
        model = User
        fields = ['full_name']


# copy from kirr.co
class UserAdminCreationForm(forms.ModelForm):
    # A form for creating new users. Includes all the required fields, plus a repeated password.
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'full_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    # A form for updating users. Includes all the fields on the user, but replaces the password field with admin's password hash display field.
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password', 'is_active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
# copy end


class GuestForm(forms.ModelForm):
    # email = forms.EmailField()
    class Meta:
        model = GuestEmail
        fields = [
            'email'
            ]

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(GuestForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        # Save the provided password in hashed format
        obj = super(GuestForm, self).save(commit=False)
        if commit:
            obj.save()
            request = self.request
            request.session['guest_email_id'] = obj.id
        return obj


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email = data.get("email")
        password = data.get("password")
        qs = User.objects.filter(email=email)
        if qs.exists():
            # check if account is activated
            not_active = qs.filter(is_active=False)
            if not_active.exists():
                link = reverse("account:resend-activation")
                reconfirm_msg = """<a href='{resend_link}'>resend activation email</a>""".format(resend_link=link)
                confirm_email = EmailActivation.objects.filter(email=email)
                is_confirmable = confirm_email.confirmable().exists()
                if is_confirmable:
                    msg = "Please check your mail box to activate your account or click to " + reconfirm_msg
                    raise forms.ValidationError(mark_safe(msg))
                email_confirm_exist = EmailActivation.objects.email_exists(email).exists()
                if email_confirm_exist:
                    msg = "Your account is not active. Click to " + reconfirm_msg
                    raise forms.ValidationError(mark_safe(msg))
                if not is_confirmable and not email_confirm_exist:
                    raise forms.ValidationError("This account is inactive. Please contact us for support.")
        user = authenticate(request, username=email, password=password)
        if user is None:
            raise forms.ValidationError("Invalid credentials")
        login(request, user)
        self.user = user
        return data



class RegisterForm(forms.ModelForm):
    # A form for creating new users. Includes all the required fields, plus a repeated password.
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'full_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords not match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False # send confirmation email to validate user
        # obj = EmailActivation.objects.create(user=user) # not a good way, moved to models.py post reciever signal
        # obj.send_activation_email()
        if commit:
            user.save()
        return user

# class RegisterForm(forms.Form):
#     username = forms.CharField()
#     email = forms.EmailField()
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
#     password_confirm = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         qs = User.objects.filter(username=username)
#         if qs.exists():
#             raise forms.ValidationError("Username is taken...")
#         return username

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         qs = User.objects.filter(email=email)
#         if qs.exists():
#             raise forms.ValidationError("Email is taken...")
#         return email

#     def clean(self):
#         data = self.cleaned_data
#         password = self.cleaned_data.get('password')
#         password_confirm = self.cleaned_data.get('password_confirm')
#         if password != password_confirm:
#             raise forms.ValidationError("Password not match!")
#         return data