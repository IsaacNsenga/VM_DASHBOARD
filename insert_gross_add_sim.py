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
file_path = "VM - 2025.xlsx"  # Chemin du fichier
sheet_name = "gross_add_sim"      # Nom de la feuille

print("✅ Chargement du fichier Excel...")
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

# Insertion des données
count = 0
print(f"📊 {len(df)} lignes à insérer...")

try:
    for index, row in df.iterrows():
        numero_mpos = int(row.iloc[0])  # Première colonne (NUMERO_MPOS)

        for col in df.columns[1:]:  # Colonnes de date
            try:
                date_releve = pd.to_datetime(col).date()
                total_gross_add = row[col]

                if pd.isna(total_gross_add):
                    continue  # Ignorer les valeurs NaN

                sql = """
                    INSERT INTO gross_add_sim (numero_mpos, date_releve, total_gross_add)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE total_gross_add = VALUES(total_gross_add)
                """
                cursor.execute(sql, (numero_mpos, date_releve, total_gross_add))
                count += 1

                if count % 500 == 0:
                    print(f"✅ {count} lignes insérées...")

            except Exception as e:
                print(f"❌ Erreur lors de l'insertion de {numero_mpos}, {col} : {e}")

    conn.commit()
    print(f"✅ Importation terminée avec succès ! {count} lignes insérées.")

except Exception as e:
    print(f"❌ Erreur générale d'insertion : {e}")

finally:
    cursor.close()
    conn.close()
    print("🔒 Connexion MySQL fermée.")
