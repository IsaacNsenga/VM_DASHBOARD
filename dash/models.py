from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')

    def __str__(self):
        return self.user.username

class Superviseur(models.Model):
    prenom = models.CharField(max_length=50)
    nom = models.CharField(max_length=50)
    adresse_mail = models.EmailField(max_length=100, unique=True)
    numero_telephone = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    class Meta:
        db_table = 'superviseur'
        managed = False

class CoachMobile(models.Model):
    numero_mpos = models.CharField(max_length=20, unique=True)
    reg_user_name = models.CharField(max_length=50)
    noms_prenoms = models.CharField(max_length=100)
    numero_cni = models.CharField(max_length=30)
    superviseur = models.ForeignKey(Superviseur, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.noms_prenoms

    class Meta:
        db_table = 'coach_mobile'
        managed = False

class AllSim(models.Model):
    numero_mpos = models.ForeignKey(
        CoachMobile,
        on_delete=models.CASCADE,
        db_column='numero_mpos'  # 🔧 Ceci corrige l'erreur !
    )
    date_releve = models.DateField()
    total_sim = models.IntegerField()

    def __str__(self):
        return f"{self.numero_mpos} - {self.date_releve}"

    class Meta:
        db_table = 'all_sim'
        unique_together = ('numero_mpos', 'date_releve')
        managed = False

class AcceptedSim(models.Model):
    numero_mpos = models.ForeignKey(
        CoachMobile,
        on_delete=models.CASCADE,
        db_column='numero_mpos'  # 🔧 Ceci corrige l'erreur !
    )
    date_releve = models.DateField()
    total_accepted = models.IntegerField()

    def __str__(self):
        return f"{self.numero_mpos} - {self.date_releve}"

    class Meta:
        db_table = 'accepted_sim'
        unique_together = ('numero_mpos', 'date_releve')
        managed = False

class GrossAddSim(models.Model):
    numero_mpos = models.ForeignKey(
        CoachMobile,
        on_delete=models.CASCADE,
        db_column='numero_mpos'  # 🔧 Ceci corrige l'erreur !
    )
    date_releve = models.DateField()
    total_gross_add = models.IntegerField()

    def __str__(self):
        return f"{self.numero_mpos} - {self.date_releve}"

    class Meta:
        db_table = 'gross_add_sim'
        unique_together = ('numero_mpos', 'date_releve')
        managed = False

class SyntheseGsm(models.Model):
    numero_mpos = models.ForeignKey(
        CoachMobile,
        on_delete=models.CASCADE,
        db_column='numero_mpos'  # 🔧 Ceci corrige l'erreur !
    )
    date_jour = models.DateField()
    total_all_sim = models.IntegerField(default=0)
    total_accepted_sim = models.IntegerField(default=0)
    taux_accepted = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_gross_add_sim = models.IntegerField(default=0)
    taux_gross_add = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    jour_presence = models.IntegerField(default=0)
    taux_presence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    drip = models.CharField(max_length=20, default='Accidental')
    productivity = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.numero_mpos} - {self.date_jour}"

    class Meta:
        db_table = 'synthese_gsm'
        unique_together = ('numero_mpos', 'date_jour')
        managed = False


class ObjectifGsm(models.Model):
    superviseur = models.OneToOneField(Superviseur, on_delete=models.CASCADE)
    mois = models.DateField(unique=True)
    objectif = models.IntegerField()

    def __str__(self):
        return f"Objectif de {self.superviseur} pour {self.mois.strftime('%B %Y')}"

    class Meta:
        db_table = 'objectif_gsm'
        managed = False

