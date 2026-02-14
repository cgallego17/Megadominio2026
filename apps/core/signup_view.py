from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm


def signup(request):
    """Vista de registro público de usuarios."""
    if request.user.is_authenticated:
        return redirect('core:panel_home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user,
                  backend='django.contrib.auth.backends.ModelBackend')
            return redirect('core:panel_home')
    else:
        form = SignupForm()

    return render(request, 'registration/signup.html', {'form': form})
