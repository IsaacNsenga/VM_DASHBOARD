import pymysql
import pandas as pd

# Dictionnaire de correspondance des superviseurs
superviseur_mapping = {
    "BANTSIMBA AYMARD": 1,
    "BATOUMOUENI JUDEL": 2,
    "BAZONZAMIO SERGES": 3,  # Remplace par le vrai nom
    "ETOU HERMAN": 4,
    "KOMBO MBOUAKA RY": 5,
    "MAHOUMA JORDEIL": 6,
    "MALONGA JOSLAIN": 7,
    "MBOUNGOU CHRIST": 8,
    "MOUKENGUE ABEL": 9,
    "TOUMBA JOB": 10
}

# Connexion à la base de données
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="dashboard",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

# Charger le fichier Excel
file_path = "VM - 20250323.xlsx"  # Remplace par le bon fichier
df = pd.read_excel(file_path, sheet_name="coach_mobile")

# Vérifier si les colonnes nécessaires existent
required_columns = ["numero_mpos", "reg_user_name", "noms_prenoms", "numero_cni", "id_superviseur"]
for col in required_columns:
    if col not in df.columns:
        print(f"❌ Erreur : La colonne '{col}' est introuvable dans le fichier Excel.")
        conn.close()
        exit()

# Nettoyer les données (supprimer les doublons et les espaces)
df = df.astype(str).apply(lambda x: x.str.strip())
df = df.drop_duplicates(subset=["numero_mpos"])

# Remplacement des noms des superviseurs par leurs ID
df["id_superviseur"] = df["id_superviseur"].map(superviseur_mapping)

# Vérifier si des superviseurs non mappés existent
if df["id_superviseur"].isnull().any():
    noms_non_mappes = df[df["id_superviseur"].isnull()]["id_superviseur"].unique()
    print(f"⚠️ Attention : Certains superviseurs ne sont pas dans la correspondance : {noms_non_mappes}")
    conn.close()
    exit()

# Nombre total de lignes
total_rows = len(df)
print(f"📊 {total_rows} Coachs Mobiles à insérer...")

# Insérer les données dans la table coach_mobile
try:
    with conn.cursor() as cursor:
        sql = """
        INSERT INTO coach_mobile (numero_mpos, reg_user_name, noms_prenoms, numero_cni, id_superviseur)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        reg_user_name = VALUES(reg_user_name), 
        noms_prenoms = VALUES(noms_prenoms), 
        numero_cni = VALUES(numero_cni), 
        id_superviseur = VALUES(id_superviseur)
        """

        count = 0
        for _, row in df.iterrows():
            cursor.execute(sql, (
                row["numero_mpos"],
                row["reg_user_name"],
                row["noms_prenoms"],
                row["numero_cni"],
                row["id_superviseur"]
            ))
            count += 1

            # Afficher une notification tous les 100 enregistrements
            if count % 100 == 0:
                print(f"✅ {count} Coachs Mobiles insérés/mis à jour...")

    conn.commit()
    print(f"🎉 Importation terminée avec succès ! {count} Coachs Mobiles insérés/mis à jour.")

except Exception as e:
    print("❌ Erreur lors de l'insertion :", e)

finally:
    conn.close()
