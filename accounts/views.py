
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):

    template_name = (
        'accounts/login.html'
    )

from .forms import RegisterForm


def register(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(
                commit=False
            )
            user.set_password(
                form.cleaned_data['password']
            )
            user.save()
            authenticated_user = authenticate(
            request,
            username=user.username,
            password=form.cleaned_data['password']
        )

            if authenticated_user:
                login(
                    request,
                    authenticated_user
                )

            return redirect(
                'dashboard'
            )

    else:

        form = RegisterForm()

    return render(
        request,
        'accounts/register.html',
        {
            'form': form
        }
    )

