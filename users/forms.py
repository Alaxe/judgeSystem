from django.contrib.auth.models import User
from django.forms import Form, CharField, PasswordInput, EmailField

from captcha.fields import ReCaptchaField

password1_kwargs = {
    'label': 'Password',
    'min_length': 6, 
    'max_length': 20,
    'widget': PasswordInput(), 
    'error_messages': { 
        'required': 'Password is required',
        'min_length': 'Password should be at least 6 characters long',
        'max_length': 'Password should be at most 30 characters long'
    }
}

password2_kwargs = {
    'label': 'Confirm password', 
    'widget': PasswordInput(),
    'error_messages': {'required': 'Confirm password'}
}

username_kwargs = {
    'label': 'User Name', 
    'min_length': 6, 
    'max_length': 30, 
    'error_messages': {
        'required': 'Username is required',
        'unique': 'Username is already used',
        'min_length': 'Username should be at least 6 characters long',
        'max_length': 'Username should be less than 30 chracters long'
    }
}

email_kwargs = {
    'label': 'E-mail', 
    'error_messages': {'required': 'E-mail is required'}
}

class LoginForm(Form):
    username = CharField(label = 'User Name',
            error_messages = {'required': 'Username is required'})
    password = CharField(label = 'Password', widget = PasswordInput(),
            error_messages = {'required': 'Password is required'})

class PasswordForm(Form):
    password1 = CharField(**password1_kwargs)
    password2 = CharField(**password2_kwargs)

    def is_valid(self):
        valid = super(PasswordForm, self).is_valid()
        
        data = self.cleaned_data
        if not data.get('password1') == data.get('password2'):
            self.add_error('password2', 'Passwords don\'t match')
            valid = False

        return valid

class RegisterForm(Form):
    username = CharField(**username_kwargs)
    email = EmailField(**email_kwargs)
    password1 = CharField(**password1_kwargs)
    password2 = CharField(**password2_kwargs)

    captcha = ReCaptchaField()

    def is_valid(self):
        valid = super(RegisterForm, self).is_valid()
        
        data = self.cleaned_data
        if not data.get('password1') == data.get('password2'):
            self.add_error('password2', 'Passwords don\'t match')
            valid = False

        if User.objects.filter(username = data.get('username')).exists():
            self.add_error('username', 'Username already taken')
            valid = False

        if User.objects.filter(email = data.get('email')).exists():
            self.add_error('email', 'Email already used')
            valid = False

        return valid

class ResetForm(Form):
     email = EmailField(**email_kwargs)

     def is_valid(self):
        valid = super(ResetForm, self).is_valid()

        email = self.cleaned_data.get('email')
        if not User.objects.filter(email = email).exists():
            self.add_error('email', 'No such email')
            valid = False
            
        return valid
