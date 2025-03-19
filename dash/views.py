from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'signin.html')


def passwordreset(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Mot de passe modifié avec succès.')
            except User.DoesNotExist:
                messages.error(request, 'Utilisateur introuvable.')
        else:
            messages.error(request, 'Les deux mots de passe ne correspondent pas.')
    return render(request, 'passwordreset.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie.')
    return redirect('signin') 

@login_required
def profil(request):

    return render(request, "profil.html")

@login_required
def home(request):
    return render(request, 'index.html')

@login_required
def vm_gsm(request):
    context = {}
    return render(request, 'vm_gsm.html', context)

@login_required
def superviseurs_gsm(request):
    context = {}
    return render(request, 'superviseurs_gsm.html', context)

@login_required
def coachs_mobiles_gsm(request):
    context = {}
    return render(request, 'coachs_mobiles_gsm.html', context)