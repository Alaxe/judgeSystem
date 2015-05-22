from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.forms import Form, CharField, PasswordInput, EmailField
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context
from django.template.loader import get_template
from django.views.generic import View 

from judge.models import Confirmation

class LoginForm(Form):
    username = CharField(label = 'User Name',
            error_messages = {'required': 'Username is required'})
    password = CharField(label = 'Password', widget = PasswordInput(),
            error_messages = {'required': 'Password is required'})

class Login(View):
    def render_form(self, request, form):
        template_name = 'judge/login.html'
        context = {'form': form}

        return render(request, template_name, context)

    def get(self, request):
        return self.render_form(request, LoginForm())

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if not form.is_valid():
            return self.render_form(request, form)

        user = authenticate(
            username = form.cleaned_data['username'], 
            password = form.cleaned_data['password'])

        if user is None:
            form.add_error('password', 
                           'Wrong username or password')

            return self.render_form(request, form)
        
        elif not user.is_active:
            form.add_error('username', 'User is not active')
            return self.render_form(request, form)

        else:
            login(request, user)
            redir_url = request.GET.get('next', reverse('judge:problem_list'))
            return HttpResponseRedirect(redir_url)

class RegisterForm(Form):
    username = CharField(label = 'User Name', min_length = 6, 
            max_length = 30, error_messages = {
            'required': 'Username is required',
            'unique': 'Username is already used',
            'min_length': 'Username should be at least \
                    6 characters long',
            'max_length': 'Username should be less \
                    than 30 chracters long'})

    email = EmailField(label = 'E-mail', error_messages = {
                'required': 'E-mail is required'})

    password1 = CharField(label = 'Password',  min_length = 6, 
            max_length = 20, widget = PasswordInput(), 
            error_messages = { 
                'required': 'Password is required',
                'min_length': 'Password should be at least \
                               6 characters long',
                'max_length': 'Password should be at most\
                               30 characters long'})

    password2 = CharField(label = 'Confirm password', 
            widget = PasswordInput(), error_messages = 
            { 'required': 'Confirm password'})

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

class Register(View):
    template_name = 'judge/register.html'

    def render(self, request):
        context = { 'form': self.form}
        return render(request, self.template_name, context)

    def get(self, request):
        self.form = RegisterForm()
        return self.render(request)
    
    def get_user(self):
        email = self.form.cleaned_data.get('email')
        username = self.form.cleaned_data.get('username')
        password = self.form.cleaned_data.get('password1')

        user = User.objects.create_user(username, email, password)
        user.is_active = False
        user.save()
        return user

    def send_conf_mail(self):
        conf_loc_url = reverse('judge:activate', args=(self.confirm.code,))
        conf_url = settings.SITE_HOST + conf_loc_url

        sender = settings.EMAIL_HOST_USER
        to = self.user.email
        subject = 'JudgeSystem account confirmation'

        plaintext = get_template('judge/confirm_email.txt')
        html      = get_template('judge/confirm_email.html')
        
        context = Context({
            'username': self.user.username, 'conf_url': conf_url})

        text_content = plaintext.render(context)
        html_content = html.render(context)

        msg = EmailMultiAlternatives(subject, text_content, sender, [to])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

    def post(self, request):
        self.form = RegisterForm(request.POST)
        
        if not self.form.is_valid():
            return self.render(request)

        self.user = self.get_user()
        self.confirm = Confirmation(user = self.user)
        self.confirm.save()

        self.send_conf_mail()

        redir_url = reverse('judge:problem_list')
        return HttpResponseRedirect(redir_url)

class Logout(View):
    def get(self, request):
        logout(request)
        url = reverse('judge:problem_list')
        return HttpResponseRedirect(url)

class Confirm(View):
    def get(self, request, code):
        confList = Confirmation.objects.filter(code = code)

        if not confList.exists():
            error_url = reverse('judge:problem_list')
            return HttpResponseRedirect(error_url)

        conf = confList[0]
        conf.delete()

        user = conf.user
        user.is_active = True
        user.save()

        redir_url = reverse('judge:login')
        return HttpResponseRedirect(redir_url)
