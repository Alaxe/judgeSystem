from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import InvalidPage, Paginator
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone
from django.views.generic import View, TemplateView

from users.models import Confirmation, PassReset
from users.forms import LoginForm, RegisterForm, ResetForm, PasswordForm

def send_email(template, context, subject, to):
    sender = settings.EMAIL_HOST_USER

    plaintext = get_template(template + '.txt')
    html = get_template(template + '.html')
    
    text_content = plaintext.render(context)
    html_content = html.render(context)

    email = EmailMultiAlternatives(subject, text_content, sender, to)
    email.attach_alternative(html_content, 'text/html')
    email.send()

class Login(View):
    def render_form(self, request, form):
        template_name = 'users/login.html'
        context = {'form': form}

        return render(request, template_name, context)
    
    def redirect_url(self, request):
        return request.GET.get('next', reverse('judge:problem_list'))

    def get(self, request):
        if request.user.is_authenticated():
            return redirect(self.redirect_url(request))
        else:
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
            return redirect(self.redirect_url(request))

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

        self.send_conf_mail()

        messageText = messages.success(request, 'You have been successfuly \
            registered. Check your e-mail for further instructions.')
        return redirect(reverse('judge:problem_list'))

class ResetPassword(View):
    template_name = 'users/password_reset.html'

    def get(self, request):
        context = {'form': ResetForm()}
        return render(request, self.template_name, context)

    def send_reset_email(self, user):
        resetQs = PassReset.objects.filter(user = user)
        if resetQs.exists():
            reset = resetQs[0]
        else:
            reset = PassReset.objects.create(user = user, created = 
                timezone.now())

        reset_loc_url = reverse('users:password_set', args=(reset.code,))
        reset_url = settings.SITE_HOST + reset_loc_url

        context = {
            'username': user.username,
            'reset_link': reset_url
        }
        
        template = 'users/email/password_reset'
        subject = 'Password reset'

        send_email(template, context, subject, [user.email])

    def post(self, request):
        form = ResetForm(request.POST)
        
        if not form.is_valid():
            context = {'form': form}
            return render(request, self.template_name, context)

        email = form.cleaned_data.get('email')
        self.send_reset_email(user = User.objects.get(email = email))

        messages.info(request, 'An email was send with instructions. If you \
            didn\' receive it make sure you entered the correct email address.')

        return redirect(reverse('judge:problem_list'))
    
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

#faking authenticate
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        messages.success(request, 'Your password has been successfuly changed.')

        return redirect(reverse('judge:problem_list'))

class Logout(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('judge:problem_list'))

class Confirm(View):
    def get(self, request, code):
        conf = get_object_or_404(Confirmation, code = code)
        conf.delete()

        user = conf.user
        user.is_active = True
        user.save()

#faking authenticate
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        messages.success(request, 'Your account has been activated')

        return redirect(reverse('judge:problem_list'))


class PasswordChange(LoginRequiredMixin, View):
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

            messages.success(request, 'Your password has been changed \
                successfully')

        context = {'passwordForm': form}
        return render(request, self.template_name, context)

class UserDetails(LoginRequiredMixin, TemplateView):
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

class UserManageForm(forms.Form):
    group_id = forms.IntegerField(widget = forms.HiddenInput)
    user_id = forms.IntegerField(widget = forms.HiddenInput)
    action = forms.CharField(widget = forms.HiddenInput)

class UserManage(PermissionRequiredMixin, View):
    template_name = 'users/user_manage.html'
    permission_required = 'auth.change_group'

    def render(self, request):
        groups = []
        for g in Group.objects.all():
            users = User.objects.filter(groups = g)
            entries = []

            for user in users: 
                entries.append({
                    'name': user.username,
                    'form': UserManageForm(initial = {
                        'group_id': g.id,
                        'user_id': user.id,
                        'action': 'remove'
                    })
                })

            groups.append({
                'name': g.name,
                'form': UserManageForm(initial = {
                    'group_id': g.id,
                    'action': 'add',
                }),
                'entries': entries,
                'users': set(users)
            })


        context = {
            'groups': groups,
            'allUsers': User.objects.all()
        }
        return render(request, self.template_name, context)
    
    def get(self, request):
        return self.render(request)

    def post(self, request):
        form = UserManageForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data

            user = get_object_or_404(User, pk = data['user_id'])
            group = get_object_or_404(Group, pk = data['group_id'])

            print(data['action'])
            if data['action'] == 'add':
                print('adding')
                user.groups.add(group)
            else:
                user.groups.remove(group)
                        
        else:
            print('nivalid')

        return self.render(request)

# if judge app is also installed
try:
    from judge.models import Solution

    class Solutions(LoginRequiredMixin, TemplateView):
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
