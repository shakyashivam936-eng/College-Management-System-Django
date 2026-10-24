from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegistrationForm


def _post_login_url(user):
    if user.role == 'REPORTER':
        return 'dashboard:issue_submit'
    return 'dashboard:index'


def login_view(request):

    if request.user.is_authenticated:
        return redirect(_post_login_url(request.user))

    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            user = form.cleaned_data['user']

            login(request, user)

            return redirect(_post_login_url(user))

    else:

        form = LoginForm()

    return render(
        request,
        'accounts/login.html',
        {
            'form': form
        }
    )


@require_POST
def logout_view(request):

    logout(request)

    return redirect('login')


@login_required
def dashboard(request):
    return render(
        request,
        'accounts/dashboard.html'
    )


def register_view(request):

    if request.user.is_authenticated:
        return redirect(_post_login_url(request.user))

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account has been created.')
            return redirect(_post_login_url(user))
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})
