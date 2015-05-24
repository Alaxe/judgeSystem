from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone
from django.views.generic import View 

from judge.models import Confirmation, PassReset

from .user_forms import LoginForm, RegisterForm, ResetForm, PasswordForm

def send_email(template, context, subject, to):
    sender = settings.EMAIL_HOST_USER

    plaintext = get_template(template + '.txt')
    html      = get_template(template + '.html')
    
    text_content = plaintext.render(context)
    html_content = html.render(context)

    msg = EmailMultiAlternatives(subject, text_content, sender, to)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

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
        template = 'judge/email/confirm_email'

        conf_loc_url = reverse('judge:activate', args=(self.confirm.code,))
        conf_url = settings.SITE_HOST + conf_loc_url

        to = [self.user.email]
        subject = 'JudgeSystem account confirmation'

        context = Context({
            'username': self.user.username, 'conf_url': conf_url})

        send_email(template, context, subject, to)

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

class ResetPassword(View):
    template_name = 'judge/password_reset.html'

    def get(self, request):
        context = {'form': ResetForm()}
        return render(request, self.template_name, context)

    def post(self, request):
        form = ResetForm(request.POST)
        
        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template_name, context)

        email = form.cleaned_data.get('email')
        
        try:
            user = User.objects.get(email = email)
            reset = PassReset(user = user)
            reset.save()

            reset_loc_url = reverse('judge:set_password', args=(reset.code,))
            reset_url = settings.SITE_HOST + reset_loc_url

            context = Context({
                'username': user.username, 'reset_link': reset_url})
            
            template = 'judge/email/password_reset'
            subject = 'Password reset'

            send_email(template, context, subject, [email])

        except User.DoesNotExist:
            pass

        redir_url = reverse('judge:problem_list')
        return HttpResponseRedirect(redir_url)
    
class SetPassword(View):
    template_name = 'judge/password_set.html'

    def get(self, request, code):
        get_object_or_404(PassReset, code = code)
        context = {'form': PasswordForm()}
        return render(request, self.template_name, context)

    def post(self, request, code):
        reset = get_object_or_404(PassReset, code = code)
        form = PasswordForm(request.POST)

        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template_name, context)

        password = form.cleaned_data.get('password1')
        user = reset.user

        user.set_password(password)
        user.save() 
        reset.delete()

        return HttpResponseRedirect(settings.LOGIN_URL)

class UserDetails(View):
    template_name = 'judge/user_details.html'

    def get(self, request):
        context = {'passwordForm': PasswordForm()}
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        form = PasswordForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data.get('password1')
            user.set_password(password)
            user.save()
            form = PasswordForm()

        context = {'passwordForm': form}
        return render(request, self.template_name, context)

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
