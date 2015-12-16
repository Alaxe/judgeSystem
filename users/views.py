from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import InvalidPage, Paginator
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone
from django.views.generic import View, TemplateView

from users.models import Confirmation, PassReset
from users.forms import LoginForm, RegisterForm, ResetForm, PasswordForm

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
        template_name = 'users/login.html'
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
    template_name = 'users/register.html'

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
        template = 'users/email/confirm_email'

        conf_loc_url = reverse('users:activate', args=(self.confirm.code,))
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

        try:
            from judge.models import UserStatts
            UserStatts(user = self.user).save()
        except ImportError:
            pass

        self.send_conf_mail()

        messageText = 'You have been successfuly registered. Check your \
                    e-mail for further instructions.'
        messages.add_message(request, messages.SUCCESS, messageText)
        redir_url = reverse('judge:problem_list')
        return HttpResponseRedirect(redir_url)

class ResetPassword(View):
    template_name = 'users/password_reset.html'

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

            try:
                reset = PassReset.objects.get(user = user)
            except PassReset.DoesNotExist:
                reset = PassReset(user = user)
                reset.created = timezone.now()
            reset.save()

            reset_loc_url = reverse('users:password_set', args=(reset.code,))
            reset_url = settings.SITE_HOST + reset_loc_url

            context = Context({
                'username': user.username, 'reset_link': reset_url})
            
            template = 'users/email/password_reset'
            subject = 'Password reset'

            send_email(template, context, subject, [email])
            
        except User.DoesNotExist:
            pass

        messageText = 'An email was send with instructions. \
                    If you didn\' receive it make sure you entered \
                    the correct email address.'
        messages.add_message(request, messages.INFO, messageText)

        redir_url = reverse('judge:problem_list')
        return HttpResponseRedirect(redir_url)
    
class SetPassword(View):
    template_name = 'users/password_set.html'

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

        messageText = 'Your password has been successfuly changed.\
                    You can now log in.'
        messages.add_message(request, messages.SUCCESS, messageText)

        return HttpResponseRedirect(settings.LOGIN_URL)

class Logout(View):
    def get(self, request):
        logout(request)
        url = reverse('judge:problem_list')
        return HttpResponseRedirect(url)

class Confirm(View):
    def get(self, request, code):
        try :
            conf = Confirmation.objects.get(code = code)
            conf.delete()

            user = conf.user
            user.is_active = True
            user.save()

            messageText = 'Your account has been confirmed.\
                           Feel free to log in.'
            messages.add_message(request, messages.SUCCESS, messageText)

            redir_url = reverse('users:login')
            return HttpResponseRedirect(redir_url)

        except Confirmation.DoesNotExist:
            error_url = reverse('judge:problem_list')
            return HttpResponseRedirect(error_url)


class PasswordChange(View):
    template_name = 'users/change_password.html'

    def get(self, request):
        context = {
                'passwordForm': PasswordForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        form = PasswordForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data.get('password1')
            user.set_password(password)
            user.save()

            user = authenticate(username = user.username, password = password)
            login(request, user)

            form = PasswordForm()

            messageText = 'Your password has been changed successfully'
            messages.add_message(request, messages.SUCCESS, messageText)

        context = {'passwordForm': form}
        return render(request, self.template_name, context)

class UserDetails(TemplateView):
    template_name = 'users/user_details.html'

    def get_context_data(self, **kwargs):
        details = [
            ('Username', self.request.user.username),
            ('E-mail', self.request.user.email)
        ]
        
        try:
            from judge.models import UserStatts
            userStatts = UserStatts.get_for_user(self.request.user)

            details.extend([
                ('Attempted problems', userStatts.tried_problems),
                ('Solved problems', userStatts.solved_problems)
            ])
        except ImportError:
            pass

        context = { 
            'details': details
        }

        return context

# if judge app is also installed
try:
    from judge.models import Solution

    class Solutions(TemplateView):
        template_name = 'users/solutions.html'

        def get_context_data(self, **kwargs):
            sol = Solution.objects.filter(user = self.request.user)
            paginator = Paginator(sol, 20)

            pageId = int(kwargs.get('page', 1))

            if pageId < 0:
                pageId = 1

            try:
                page = paginator.page(pageId)
            except InvalidPage:
                raise Http404

            return { 'page': page }

except ImportError:
    pass
