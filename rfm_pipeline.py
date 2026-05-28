# ============================================================
#  PROJET FINAL - Algo & BDD
#  MSc2 Manager Data Marketing - INSEEC
#  Script : Pipeline Python - RFM + API + MySQL
# ============================================================

import os
import pandas as pd
import mysql.connector
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Crée et retourne une connexion MySQL."""
    conn = mysql.connector.connect(
        host     = os.getenv("DB_HOST",     "127.0.0.1"),
        port     = int(os.getenv("DB_PORT", "3306")),
        user     = os.getenv("DB_USER",     "root"),
        password = os.getenv("DB_PASSWORD", ""),
        database = os.getenv("DB_NAME",     "ecommerce_rfm")
    )
    print("✅ Connexion MySQL établie")
    return conn

def load_data(conn):
    """Charge les données de commandes depuis MySQL."""
    query = """
        SELECT
            c.customer_id,
            c.customer_city,
            c.customer_state,
            o.order_id,
            o.order_purchase_timestamp,
            o.order_status,
            p.payment_value,
            p.payment_type
        FROM customers c
        JOIN orders o         ON c.customer_id = o.customer_id
        JOIN order_payments p ON o.order_id    = p.order_id
        WHERE o.order_status != 'canceled'
    """
    df = pd.read_sql(query, conn)
    print(f"✅ Données chargées : {len(df)} lignes, {df['customer_id'].nunique()} clients uniques")
    return df

def get_exchange_rate(base_currency="BRL", target_currency="EUR"):
    """Appelle l'API exchangerate-api pour obtenir le taux BRL → EUR."""
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        rate = data["rates"][target_currency]
        print(f"✅ Taux de change {base_currency}→{target_currency} : {rate:.4f}")
        return rate
    except Exception as e:
        print(f"⚠️  API indisponible ({e}), taux par défaut 0.17")
        return 0.17

def compute_rfm(df, reference_date=None):
    """Calcule les scores RFM pour chaque client."""
    if reference_date is None:
        reference_date = datetime.now()

    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

    rfm = df.groupby("customer_id").agg(
        derniere_commande = ("order_purchase_timestamp", "max"),
        frequency         = ("order_id",                 "nunique"),
        monetary          = ("payment_value",             "sum")
    ).reset_index()

    rfm["recency_days"] = (reference_date - rfm["derniere_commande"]).dt.days
    rfm = rfm.drop(columns=["derniere_commande"])
    rfm["monetary"] = rfm["monetary"].round(2)

    rfm["r_score"] = pd.qcut(rfm["recency_days"], q=4, labels=[4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"),  q=4, labels=[1, 2, 3, 4]).astype(int)

    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]
    rfm["segment"]   = rfm.apply(assign_segment, axis=1)

    print(f"✅ RFM calculé pour {len(rfm)} clients")
    print(rfm["segment"].value_counts().to_string())
    return rfm

def assign_segment(row):
    """Attribue un segment marketing selon les scores RFM."""
    r, f, m = row["r_score"], row["f_score"], row["m_score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif f >= 3 and m >= 3:
        return "Loyal"
    elif r >= 3 and f <= 2:
        return "Potentiel"
    elif r <= 2 and f >= 3:
        return "A risque"
    elif row["rfm_score"] <= 5:
        return "Dormants"
    else:
        return "Nouveaux clients"

def enrich_with_currency(rfm_df, rate):
    """Ajoute une colonne monetary_eur (conversion BRL → EUR)."""
    rfm_df["monetary_eur"] = (rfm_df["monetary"] * rate).round(2)
    print(f"✅ Colonne monetary_eur ajoutée")
    return rfm_df

def save_rfm_to_db(conn, rfm_df):
    """Insère les résultats RFM dans la table rfm_segments."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rfm_segments")

    insert_query = """
        INSERT INTO rfm_segments
            (customer_id, recency_days, frequency, monetary,
             r_score, f_score, m_score, rfm_score, segment)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            recency_days = VALUES(recency_days),
            frequency    = VALUES(frequency),
            monetary     = VALUES(monetary),
            r_score      = VALUES(r_score),
            f_score      = VALUES(f_score),
            m_score      = VALUES(m_score),
            rfm_score    = VALUES(rfm_score),
            segment      = VALUES(segment),
            computed_at  = CURRENT_TIMESTAMP
    """
    rows = [
        (row["customer_id"], int(row["recency_days"]), int(row["frequency"]),
         float(row["monetary"]), int(row["r_score"]), int(row["f_score"]),
         int(row["m_score"]), int(row["rfm_score"]), row["segment"])
        for _, row in rfm_df.iterrows()
    ]
    cursor.executemany(insert_query, rows)
    conn.commit()
    print(f"✅ {cursor.rowcount} lignes insérées dans rfm_segments")
    cursor.close()

def print_summary(rfm_df):
    """Affiche un résumé des segments dans le terminal."""
    print("\n" + "="*50)
    print("  RÉSUMÉ SEGMENTATION RFM")
    print("="*50)
    summary = rfm_df.groupby("segment").agg(
        nb_clients   = ("customer_id", "count"),
        recence_moy  = ("recency_days", "mean"),
        freq_moy     = ("frequency",    "mean"),
        ca_moyen_eur = ("monetary_eur", "mean")
    ).round(1)
    print(summary.to_string())
    print("="*50 + "\n")

if __name__ == "__main__":
    print("\n🚀 Démarrage du pipeline RFM...\n")
    conn   = get_connection()
    df     = load_data(conn)
    rate   = get_exchange_rate(base_currency="BRL", target_currency="EUR")
    rfm_df = compute_rfm(df, reference_date=datetime(2018, 10, 1))
    rfm_df = enrich_with_currency(rfm_df, rate)
    save_rfm_to_db(conn, rfm_df)
    print_summary(rfm_df)
    conn.close()
    print("✅ Pipeline terminé avec succès !\n")