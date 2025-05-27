from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.db import models
import plotly.graph_objs as go
from collections import Counter
from django.db.models import Sum, Max 
import json
from django.db.models.functions import TruncMonth
from datetime import datetime
from .models import Notification, supervisor_report, SyntheseGsm, AllSim, CoachMobile, GrossAddSim
import openpyxl
from django.http import HttpResponse
from django.utils.timezone import now
from django.utils.timesince import timesince


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
    # Agréger les gross add par mois
    gross_adds_par_mois = (
        SyntheseGsm.objects
        .annotate(mois=TruncMonth('date_jour'))
        .values('mois')
        .annotate(total_gross_add=Sum('total_gross_add_sim'))
        .order_by('mois')
    )

    # Transformer pour le frontend
    labels = [g['mois'].strftime('%B %Y') for g in gross_adds_par_mois]
    data = [g['total_gross_add'] for g in gross_adds_par_mois]

    context = {
        'gross_add_labels': json.dumps(labels),  # Convertir en JSON string
        'gross_add_data': json.dumps(data),      # Convertir en JSON string
    }

    return render(request, 'vm_gsm.html', context)

@login_required
def superviseurs_gsm(request):
    context = {}
    return render(request, 'superviseurs_gsm.html', context)

@login_required
def coachs_mobiles_gsm(request):
    context = {}
    return render(request, 'coachs_mobiles_gsm.html', context)

@login_required
def formulaire_rapport(request):
    if request.method == 'POST':
        full_name = request.user.get_full_name() or request.user.username
        date_enregistrement = request.POST.get('date_enregistrement')
        lieu_activite = request.POST.get('lieu_activite')

        if not date_enregistrement or not lieu_activite:
            messages.error(request, "Erreur : le rapport n'a pas pu être soumis.")
            return redirect('formulaire_rapport')

        try:
            rapport = supervisor_report(
                user=request.user,
                full_name=full_name,
                date_enregistrement=date_enregistrement,
                lieu_activite=lieu_activite,
                stock_sim_activees=request.POST.get('stock_sim_activees') or 0,
                stock_sim_blanches=request.POST.get('stock_sim_blanches') or 0,
                sim_appro=request.POST.get('sim_appro') or 0,
                gsm=request.POST.get('gsm') or 0,
                momo_app=request.POST.get('momo_app') or 0,
                mymtn=request.POST.get('mymtn') or 0,
                ayoba=request.POST.get('ayoba') or 0,
                telephone=request.POST.get('telephone') or 0,
                modem=request.POST.get('modem') or 0,
                mifi=request.POST.get('mifi') or 0,
                wifix=request.POST.get('wifix') or 0,
                difficulte=request.POST.get('difficulte') or "",
                momo_convertion=request.POST.get('momo_convertion') or 0,
                resetpin=request.POST.get('resetpin') or 0,
                prospection_ca=request.POST.get('prospection_ca') or 0,
                besoin=request.POST.get('besoin') or "",
                concurrentielle=request.POST.get('concurrentielle') or ""
            )
            rapport.save()

            # 💬 Création de la notification
            Notification.objects.create(
                user=request.user,
                report_date=rapport.date_enregistrement
            )

            messages.success(request, "Rapport enregistré avec succès !")
        except Exception as e:
            messages.error(request, "Erreur : le rapport n'a pas pu être soumis.")
        return redirect('formulaire_rapport')

    return render(request, 'formulaire_rapport.html')

@login_required
def historique_rapport(request):
    # Récupérer tous les rapports, ordonnés par date_created décroissante
    rapports = supervisor_report.objects.all().order_by('-date_created')

    # ⏰ Charger les notifications
    notifications = Notification.objects.select_related('user').order_by('-created_at')[:5]
    for notif in notifications:
        notif.elapsed = timesince(notif.created_at, now())  # Exemple : "15 minutes"


    # Récupérer les paramètres GET pour filtrer
    superviseur = request.GET.get('superviseur')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')

    # Appliquer les filtres si présents
    if superviseur:
        rapports = rapports.filter(full_name__iexact=superviseur)
    if date_debut:
        rapports = rapports.filter(date_enregistrement__gte=date_debut)
    if date_fin:
        rapports = rapports.filter(date_enregistrement__lte=date_fin)

    # Export Excel si demandé
    if request.GET.get('export') == '1':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Rapports"

        headers = [
            "Nom complet", "Date", "Lieu activité", "SIM activées", "SIM blanches",
            "SIM appro", "GSM", "MoMo App", "MyMTN", "Ayoba", "Téléphone", "Modem",
            "MiFi", "WiFix", "Difficulté", "Conversion MoMo", "Reset PIN",
            "Prospection CA", "Besoins", "Concurrence", "Date Création"
        ]
        ws.append(headers)

        for r in rapports:
            ws.append([
                r.full_name,
                r.date_enregistrement.strftime('%Y-%m-%d') if r.date_enregistrement else '',
                r.lieu_activite,
                r.stock_sim_activees,
                r.stock_sim_blanches,
                r.sim_appro,
                r.gsm,
                r.momo_app,
                r.mymtn,
                r.ayoba,
                r.telephone,
                r.modem,
                r.mifi,
                r.wifix,
                r.difficulte,
                r.momo_convertion,
                r.resetpin,
                r.prospection_ca,
                r.besoin,
                r.concurrentielle,
                r.date_created.strftime('%Y-%m-%d %H:%M:%S') if r.date_created else '',
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=rapports.xlsx'
        wb.save(response)
        return response

    # Liste des superviseurs distincts pour le filtre (ordre alphabétique)
    superviseurs = supervisor_report.objects.values_list('full_name', flat=True).distinct().order_by('full_name')

    context = {
        'rapports': rapports,
        'superviseurs': superviseurs,
        'filtre_superviseur': superviseur,
        'filtre_date_debut': date_debut,
        'filtre_date_fin': date_fin,
        'notifications': notifications,  # 📩 ajouter au contexte
    }

    return render(request, 'historique_rapport.html', context)


