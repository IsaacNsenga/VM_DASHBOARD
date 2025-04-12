from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.db import models
from .models import SyntheseGsm, AllSim, CoachMobile, GrossAddSim
import plotly.graph_objs as go
from collections import Counter
from django.db.models import Sum, Max 
from datetime import datetime, timedelta

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
    # -- CARDS KPI --
    summary_date = request.GET.get('summary_date')
    if not summary_date:
        latest_entry = SyntheseGsm.objects.order_by('-date_jour').first()
        if latest_entry:
            summary_date = latest_entry.date_jour.strftime('%Y-%m-%d')

    summary_qs = SyntheseGsm.objects.all()
    if summary_date:
        summary_qs = summary_qs.filter(date_jour=summary_date)

    total_all_sim = summary_qs.aggregate(Sum('total_all_sim'))['total_all_sim__sum'] or 0
    total_accepted_sim = summary_qs.aggregate(Sum('total_accepted_sim'))['total_accepted_sim__sum'] or 0
    total_gross_add_sim = summary_qs.aggregate(Sum('total_gross_add_sim'))['total_gross_add_sim__sum'] or 0

    # Calculs des taux
    accepted_rate = 0
    gross_add_rate = 0

    if total_accepted_sim:
        accepted_rate = (total_accepted_sim / total_all_sim) * 100 if total_all_sim else 0
        gross_add_rate = (total_gross_add_sim / total_accepted_sim) * 100

    accepted_class = "text-danger"
    if accepted_rate >= 95:
        accepted_class = "text-success"
    elif accepted_rate > 90:
        accepted_class = "text-warning"

    gross_add_class = "text-danger"
    if gross_add_rate >= 95:
        gross_add_class = "text-success"
    elif gross_add_rate > 90:
        gross_add_class = "text-warning"

    # -- DRIP FILTER --
    selected_date_drip = request.GET.get('selected_date_drip')
    drip_qs = SyntheseGsm.objects.all()
    if not selected_date_drip:
        latest_drip_entry = drip_qs.order_by('-date_jour').first()
        if latest_drip_entry:
            selected_date_drip = latest_drip_entry.date_jour.strftime('%Y-%m-%d')
    if selected_date_drip:
        drip_qs = drip_qs.filter(date_jour=selected_date_drip)

    drip_data = drip_qs.values_list('drip', flat=True)
    drip_counts = Counter(drip_data)
    labels = list(drip_counts.keys())
    values = list(drip_counts.values())

    pie_chart = go.Figure(
        data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            hoverinfo="label+percent+value",
            textinfo="label+percent",
            textfont=dict(size=10),
            marker=dict(colors=['#191970', '#FF8C00', '#006400', '#0fa3ff', '#800080']),
            sort=False
        )]
    )
    pie_chart.update_layout(
        height=300,
        margin=dict(t=30, b=30, l=10, r=10),
        legend=dict(
            orientation="h",
            y=-0.2,
            x=0.5,
            xanchor="center",
            yanchor="top",
            font=dict(size=8)
        )
    )
    drip_chart_html = pie_chart.to_html(full_html=False)

    # -- PRODUCTIVITY FILTER --
    selected_date_productivity = request.GET.get('selected_date_productivity')
    productivity_qs = SyntheseGsm.objects.all()
    if not selected_date_productivity:
        latest_productivity_entry = productivity_qs.order_by('-date_jour').first()
        if latest_productivity_entry:
            selected_date_productivity = latest_productivity_entry.date_jour.strftime('%Y-%m-%d')
    if selected_date_productivity:
        productivity_qs = productivity_qs.filter(date_jour=selected_date_productivity)

    productivity_per_drip = productivity_qs.values('drip').annotate(avg_productivity=models.Avg('productivity'))
    bar_labels = [entry['drip'] for entry in productivity_per_drip]
    bar_values = [float(entry['avg_productivity']) for entry in productivity_per_drip]

    bar_chart = go.Figure(
        data=[go.Bar(
            x=bar_labels,
            y=bar_values,
            marker_color='#4682B4',
            text=[f"{v:.2f}" for v in bar_values],
            textposition='auto'
        )]
    )
    bar_chart.update_layout(
        height=300,
        margin=dict(t=30, b=30, l=10, r=10),
        xaxis_title='Drip',
        yaxis_title='Moyenne Productivité',
        font=dict(size=10)
    )
    productivity_chart_html = bar_chart.to_html(full_html=False)

    # -- GRAPHE COMBINE : GROSS ADD + TAUX CM ACTIFS --
    # Récupération des dates dans l'URL (GET)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Si rien n'est fourni : période = tout le mois courant jusqu'à la dernière date disponible
    if not start_date or not end_date:
        today = datetime.today()
        first_day = today.replace(day=1).date()

        latest_date = AllSim.objects.aggregate(max_date=Max('date_releve'))['max_date']
        if not latest_date:
            latest_date = today.date()

        start_date = start_date or first_day.strftime('%Y-%m-%d')
        end_date = end_date or latest_date.strftime('%Y-%m-%d')

    # Récupération des dates distinctes dans la période
    filtered_dates = AllSim.objects.filter(
        date_releve__range=[start_date, end_date]
    ).values_list('date_releve', flat=True).distinct().order_by('date_releve')

    # Données Gross Add agrégées
    grossadd_data = GrossAddSim.objects.filter(
        date_releve__range=[start_date, end_date]
    ).values('date_releve').annotate(total_gross_add=Sum('total_gross_add'))

    # Calcul des valeurs pour le graphique
    total_cm = CoachMobile.objects.count()
    taux_actifs = []
    gross_add_values = []
    x_dates = []

    for date in filtered_dates:
        nb_actifs = AllSim.objects.filter(
            date_releve=date,
            total_sim__gt=0
        ).values('numero_mpos').distinct().count()

        taux = (nb_actifs / total_cm) * 100 if total_cm > 0 else 0
        taux_actifs.append(round(taux, 2))
        x_dates.append(date)

        gross_add = next(
            (item['total_gross_add'] for item in grossadd_data if item['date_releve'] == date),
            0
        )
        gross_add_values.append(gross_add)

    # Construction du graphique combiné
    combo_chart = go.Figure()

    # Barres pour Gross Add
    combo_chart.add_trace(go.Bar(
        x=x_dates,
        y=gross_add_values,
        name='Gross Add Sim',
        marker_color='#4682B4',
        yaxis='y1'
    ))

    # Ligne pour taux CM actifs
    combo_chart.add_trace(go.Scatter(
        x=x_dates,
        y=taux_actifs,
        name='Taux CM Actifs (%)',
        mode='lines+markers',
        line=dict(color='orange'),
        yaxis='y2'
    ))

    # Mise en forme du graphique
    combo_chart.update_layout(
        xaxis=dict(title='Date'),
        yaxis=dict(title='Gross Add Sim', side='left', showgrid=False),
        yaxis2=dict(
            title='Taux CM Actifs (%)',
            overlaying='y',
            side='right',
            showgrid=False,
            range=[0, 100]
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        height=500,
        margin=dict(t=30, b=30, l=50, r=50),
        legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.2)
    )

    combo_chart_html = combo_chart.to_html(full_html=False)
    
    context = {
        'summary_date': summary_date,
        'total_all_sim': total_all_sim,
        'total_accepted_sim': total_accepted_sim,
        'total_gross_add_sim': total_gross_add_sim,
        'accepted_rate': accepted_rate,
        'gross_add_rate': gross_add_rate,
        'accepted_class': accepted_class,
        'gross_add_class': gross_add_class,
        'drip_chart': drip_chart_html,
        'productivity_chart': productivity_chart_html,
        'selected_date_drip': selected_date_drip,
        'selected_date_productivity': selected_date_productivity,
        'combo_chart': combo_chart_html,
        'start_date': start_date,
        'end_date': end_date,

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