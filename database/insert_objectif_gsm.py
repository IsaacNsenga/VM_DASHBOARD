import pymysql
import pandas as pd
from datetime import datetime

# Dictionnaire de correspondance des superviseurs
superviseur_mapping = {
    "BANTSIMBA AYMARD": 1,
    "BATOUMOUENI JUDEL": 2,
    "BAZONZAMIO SERGES": 3,
    "ETOU HERMAN": 4,
    "KOMBO MBOUAKA RY": 5,
    "MAHOUMA JORDEIL": 6,
    "MALONGA JOSLAIN": 7,
    "MBOUNGOU CHRIST": 8,
    "MOUKENGUE ABEL": 9,
    "TOUMBA JOB": 10
}

# Connexion à la base de données
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "dashboard",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

# Charger le fichier Excel
file_path = "VM - 2025.xlsx"
sheet_name = "objectif_gsm"
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Nettoyer les données
df.fillna(0, inplace=True)
df.columns = [str(col).strip() for col in df.columns]  # Nettoyage des noms de colonnes
df["superviseur"] = df["superviseur"].astype(str).str.strip()

# Connexion à la base de données
try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ Connexion réussie à MySQL.")
except Exception as e:
    print(f"❌ Erreur de connexion : {e}")
    exit()

# Nombre total d'objectifs à insérer
nb_inserted = 0

# Colonnes de mois (tout sauf 'superviseur')
mois_columns = [col for col in df.columns if col != "superviseur"]

try:
    for index, row in df.iterrows():
        superviseur_nom = row["superviseur"]

        if superviseur_nom not in superviseur_mapping:
            print(f"⚠️ Superviseur non mappé : {superviseur_nom}")
            continue

        superviseur_id = superviseur_mapping[superviseur_nom]

        for col in mois_columns:
            try:
                # Convertir le nom de colonne en date
                mois = pd.to_datetime(col).date()
                objectif = int(row[col])

                sql = """
                    INSERT INTO objectif_gsm (superviseur_id, mois, objectif)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE objectif = VALUES(objectif)
                """
                cursor.execute(sql, (superviseur_id, mois, objectif))
                nb_inserted += 1

                if nb_inserted % 100 == 0:
                    print(f"✅ {nb_inserted} objectifs insérés...")

            except Exception as e:
                print(f"❌ Erreur pour {superviseur_nom}, colonne {col} : {e}")

    conn.commit()
    print(f"🎯 {nb_inserted} objectifs insérés avec succès.")

except Exception as e:
    print(f"❌ Erreur globale : {e}")

finally:
    cursor.close()
    conn.close()
    print("🔒 Connexion fermée.")
