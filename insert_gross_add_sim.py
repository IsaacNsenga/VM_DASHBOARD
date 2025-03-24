import pymysql
import pandas as pd
from datetime import datetime

# Paramètres de connexion MySQL
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Mets ton mot de passe MySQL si nécessaire
    "database": "dashboard",
    "charset": "utf8mb4"
}

# Charger le fichier Excel
file_path = "VM - 20250323.xlsx"  # Mets le bon fichier
sheet_name = "gross_add_sim"  # Mets le bon nom de feuille

print("✅ Chargement du fichier Excel...")
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Connexion à MySQL
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()
print("✅ Connexion MySQL réussie.")

# Nombre total de lignes
total_rows = len(df)
print(f"📊 {total_rows} lignes à insérer...")

# Insertion des données
count = 0
for index, row in df.iterrows():
    numero_mpos = row.iloc[0]  # Première colonne (NUMERO_MPOS)

    for col in df.columns[1:]:  # Toutes les colonnes sauf la première
        try:
            date_releve = pd.to_datetime(col).date()  # Convertir en date
            total_gross_add = row[col]  # Récupérer la valeur correspondante

            sql = """
                INSERT INTO gross_add_sim (numero_mpos, date_releve, total_gross_add)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE total_gross_add = VALUES(total_gross_add)
            """
            
            cursor.execute(sql, (numero_mpos, date_releve, total_gross_add))
            count += 1

            # Afficher une notification tous les 500 insertions
            if count % 500 == 0:
                print(f"✅ {count} lignes insérées/mises à jour...")

        except Exception as e:
            print(f"❌ Erreur pour {numero_mpos}, {col}: {e}")
            continue

# Valider et fermer la connexion
conn.commit()
cursor.close()
conn.close()

print(f"✅ Importation terminée avec succès ! {count} lignes insérées/mises à jour.")
