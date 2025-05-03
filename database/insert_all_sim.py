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
file_path = "VM - 2025.xlsx"  # Mets le chemin correct
sheet_name = "all_sim"  # Feuille à importer

df = pd.read_excel(file_path, sheet_name=sheet_name)
print("✅ Fichier Excel chargé avec succès.")

# Connexion à MySQL
try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ Connexion MySQL réussie.")
except Exception as e:
    print(f"❌ Erreur de connexion MySQL : {e}")
    exit()

# Transformation des données et insertion
nb_lignes = 0
print(f"📊 {len(df)} lignes à insérer...")

try:
    for index, row in df.iterrows():
        numero_mpos = int(row.iloc[0]) # Première colonne (NUMERO_MPOS)

        for col in df.columns[1:]:  # Toutes les colonnes sauf la première
            try:
                date_releve = pd.to_datetime(col).date()  # Convertir en date
                total_sim = row[col]  # Valeur correspondante
                
                if pd.isna(total_sim):
                    continue  # Ignorer les valeurs NaN
                
                sql = """
                    INSERT INTO all_sim (numero_mpos, date_releve, total_sim)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE total_sim = VALUES(total_sim)
                """
                cursor.execute(sql, (numero_mpos, date_releve, total_sim))
                nb_lignes += 1
                
                if nb_lignes % 500 == 0:
                    print(f"✅ {nb_lignes} lignes insérées...")
            except Exception as e:
                print(f"❌ Erreur lors de l'insertion de {numero_mpos}, {col} : {e}")

    conn.commit()
    print(f"✅ Importation terminée avec succès ! {nb_lignes} lignes insérées.")
except Exception as e:
    print(f"❌ Erreur générale d'insertion : {e}")
finally:
    cursor.close()
    conn.close()
    print("🔒 Connexion MySQL fermée.")
