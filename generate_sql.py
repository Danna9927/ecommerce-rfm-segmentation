# ============================================================
#  PROJET FINAL - Algo & BDD
#  Script : Génération du SQL depuis les vrais CSV Olist
#  Extrait 200 clients, 500 commandes réelles
# ============================================================

import pandas as pd
import os

# ============================================================
# 1. CHARGEMENT DES CSV
# ============================================================

print("📂 Chargement des CSV...")

customers = pd.read_csv("olist_customers_dataset.csv")
orders    = pd.read_csv("olist_orders_dataset.csv")
items     = pd.read_csv("olist_order_items_dataset.csv")
payments  = pd.read_csv("olist_order_payments_dataset.csv")
products  = pd.read_csv("olist_products_dataset.csv")

print(f"✅ Clients : {len(customers)}")
print(f"✅ Commandes : {len(orders)}")
print(f"✅ Produits : {len(products)}")

# ============================================================
# 2. FILTRAGE — On prend 200 clients avec commandes livrées
# ============================================================

# On garde seulement les commandes livrées
orders_delivered = orders[orders["order_status"] == "delivered"].copy()

# On prend les 200 premiers clients qui ont au moins une commande livrée
customers_with_orders = orders_delivered["customer_id"].unique()[:200]
customers_sample = customers[customers["customer_id"].isin(customers_with_orders)].head(200)

# On prend les commandes de ces clients
orders_sample = orders_delivered[orders_delivered["customer_id"].isin(customers_sample["customer_id"])]

# On prend les items de ces commandes
items_sample = items[items["order_id"].isin(orders_sample["order_id"])]

# On prend les produits concernés
products_ids = items_sample["product_id"].unique()
products_sample = products[products["product_id"].isin(products_ids)]

# On prend les paiements de ces commandes
payments_sample = payments[payments["order_id"].isin(orders_sample["order_id"])]

print(f"\n📊 Extrait sélectionné :")
print(f"   Clients   : {len(customers_sample)}")
print(f"   Commandes : {len(orders_sample)}")
print(f"   Produits  : {len(products_sample)}")
print(f"   Items     : {len(items_sample)}")
print(f"   Paiements : {len(payments_sample)}")

# ============================================================
# 3. NETTOYAGE DES DONNÉES
# ============================================================

# Nettoyage customers
customers_sample = customers_sample[["customer_id", "customer_city", "customer_state"]].copy()
customers_sample["customer_city"]  = customers_sample["customer_city"].str.replace("'", "''")
customers_sample["customer_state"] = customers_sample["customer_state"].fillna("XX")

# Nettoyage products
products_sample = products_sample[["product_id", "product_category_name", "product_weight_g",
                                    "product_length_cm", "product_height_cm", "product_width_cm"]].copy()
products_sample["product_category_name"] = products_sample["product_category_name"].fillna("outros").str.replace("'", "''")
products_sample = products_sample.fillna(0)

# Nettoyage orders
orders_sample = orders_sample[["order_id", "customer_id", "order_status",
                                "order_purchase_timestamp", "order_delivered_customer_date"]].copy()
orders_sample["order_purchase_timestamp"]      = pd.to_datetime(orders_sample["order_purchase_timestamp"])
orders_sample["order_delivered_customer_date"] = pd.to_datetime(orders_sample["order_delivered_customer_date"])

# Nettoyage items
items_sample = items_sample[["order_id", "product_id", "order_item_id",
                               "seller_id", "price", "freight_value"]].copy()
items_sample = items_sample.fillna(0)

# Nettoyage payments
payments_sample = payments_sample[["order_id", "payment_sequential", "payment_type",
                                    "payment_installments", "payment_value"]].copy()
payments_sample = payments_sample.fillna(0)

# ============================================================
# 4. GÉNÉRATION DU FICHIER SQL
# ============================================================

print("\n📝 Génération du fichier SQL...")

lines = []

lines.append("-- ============================================================")
lines.append("--  PROJET FINAL - Algo & BDD")
lines.append("--  MSc2 Manager Data Marketing - INSEEC")
lines.append("--  Dataset : Olist Brazilian E-Commerce (données réelles)")
lines.append("--  Sujet   : Segmentation client RFM")
lines.append("-- ============================================================")
lines.append("")
lines.append("DROP DATABASE IF EXISTS ecommerce_rfm;")
lines.append("CREATE DATABASE ecommerce_rfm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
lines.append("USE ecommerce_rfm;")
lines.append("")

# Tables
lines.append("""CREATE TABLE customers (
    customer_id     VARCHAR(50)  NOT NULL,
    customer_city   VARCHAR(100) NOT NULL,
    customer_state  VARCHAR(5)   NOT NULL,
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_customers PRIMARY KEY (customer_id)
);""")

lines.append("""CREATE TABLE products (
    product_id          VARCHAR(50)  NOT NULL,
    product_category    VARCHAR(100) NOT NULL,
    product_weight_g    DECIMAL(10,2),
    product_length_cm   DECIMAL(10,2),
    product_height_cm   DECIMAL(10,2),
    product_width_cm    DECIMAL(10,2),
    CONSTRAINT pk_products PRIMARY KEY (product_id)
);""")

lines.append("""CREATE TABLE orders (
    order_id                    VARCHAR(50)  NOT NULL,
    customer_id                 VARCHAR(50)  NOT NULL,
    order_status                VARCHAR(30)  NOT NULL,
    order_purchase_timestamp    TIMESTAMP    NOT NULL,
    order_delivered_timestamp   TIMESTAMP    NULL,
    CONSTRAINT pk_orders        PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_cust   FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);""")

lines.append("""CREATE TABLE order_items (
    order_id        VARCHAR(50)    NOT NULL,
    product_id      VARCHAR(50)    NOT NULL,
    order_item_id   INT            NOT NULL,
    seller_id       VARCHAR(50),
    price           DECIMAL(10,2)  NOT NULL,
    freight_value   DECIMAL(10,2)  NOT NULL DEFAULT 0,
    CONSTRAINT pk_order_items      PRIMARY KEY (order_id, product_id, order_item_id),
    CONSTRAINT fk_items_order      FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    CONSTRAINT fk_items_product    FOREIGN KEY (product_id) REFERENCES products(product_id)
);""")

lines.append("""CREATE TABLE order_payments (
    order_id            VARCHAR(50)   NOT NULL,
    payment_sequential  INT           NOT NULL,
    payment_type        VARCHAR(30)   NOT NULL,
    payment_installments INT          NOT NULL DEFAULT 1,
    payment_value       DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_payments     PRIMARY KEY (order_id, payment_sequential),
    CONSTRAINT fk_pay_order    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);""")

lines.append("""CREATE TABLE rfm_segments (
    customer_id     VARCHAR(50)   NOT NULL,
    recency_days    INT           NOT NULL,
    frequency       INT           NOT NULL,
    monetary        DECIMAL(10,2) NOT NULL,
    r_score         INT           NOT NULL,
    f_score         INT           NOT NULL,
    m_score         INT           NOT NULL,
    rfm_score       INT           NOT NULL,
    segment         VARCHAR(50)   NOT NULL,
    computed_at     TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_rfm          PRIMARY KEY (customer_id),
    CONSTRAINT fk_rfm_cust     FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);""")

# Vues et procédures
lines.append("""CREATE OR REPLACE VIEW vue_client_resume AS
SELECT
    c.customer_id, c.customer_city, c.customer_state,
    COUNT(DISTINCT o.order_id)     AS nb_commandes,
    ROUND(SUM(p.payment_value), 2) AS ca_client,
    ROUND(AVG(p.payment_value), 2) AS panier_moyen,
    MAX(o.order_purchase_timestamp) AS derniere_commande,
    DATEDIFF(CURDATE(), MAX(o.order_purchase_timestamp)) AS jours_depuis_achat
FROM customers c
LEFT JOIN orders o         ON c.customer_id = o.customer_id
LEFT JOIN order_payments p ON o.order_id    = p.order_id
WHERE o.order_status != 'canceled' OR o.order_status IS NULL
GROUP BY c.customer_id, c.customer_city, c.customer_state;""")

lines.append("DELIMITER $$")
lines.append("""CREATE PROCEDURE GetTopClients(IN p_limit INT, IN p_state VARCHAR(5))
BEGIN
    SELECT c.customer_id, c.customer_city, c.customer_state,
           COUNT(DISTINCT o.order_id) AS nb_commandes,
           ROUND(SUM(p.payment_value), 2) AS ca_total
    FROM customers c
    JOIN orders o         ON c.customer_id = o.customer_id
    JOIN order_payments p ON o.order_id    = p.order_id
    WHERE o.order_status = 'delivered'
      AND (p_state IS NULL OR c.customer_state = p_state)
    GROUP BY c.customer_id, c.customer_city, c.customer_state
    ORDER BY ca_total DESC
    LIMIT p_limit;
END$$""")
lines.append("DELIMITER ;")
lines.append("")

# INSERT customers
lines.append("-- ============================================================")
lines.append("-- INSERTION DES DONNÉES RÉELLES")
lines.append("-- ============================================================")
lines.append("")

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

# Customers
lines.append("INSERT INTO customers (customer_id, customer_city, customer_state) VALUES")
rows = []
for _, r in customers_sample.iterrows():
    rows.append(f"('{r['customer_id']}', '{r['customer_city']}', '{r['customer_state']}')")
lines.append(",\n".join(rows) + ";")
lines.append("")

# Products
lines.append("INSERT INTO products (product_id, product_category, product_weight_g, product_length_cm, product_height_cm, product_width_cm) VALUES")
rows = []
for _, r in products_sample.iterrows():
    rows.append(f"('{r['product_id']}', '{r['product_category_name']}', {r['product_weight_g']}, {r['product_length_cm']}, {r['product_height_cm']}, {r['product_width_cm']})")
lines.append(",\n".join(rows) + ";")
lines.append("")

# Orders - par batch de 100
all_order_rows = []
for _, r in orders_sample.iterrows():
    ts  = r["order_purchase_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    del_date = r["order_delivered_customer_date"]
    if pd.isnull(del_date):
        delivered = "NULL"
    else:
        delivered = f"'{del_date.strftime('%Y-%m-%d %H:%M:%S')}'"
    all_order_rows.append(f"('{r['order_id']}', '{r['customer_id']}', '{r['order_status']}', '{ts}', {delivered})")

for batch in chunks(all_order_rows, 100):
    lines.append("INSERT INTO orders (order_id, customer_id, order_status, order_purchase_timestamp, order_delivered_timestamp) VALUES")
    lines.append(",\n".join(batch) + ";")
lines.append("")

# Items - par batch de 100
all_item_rows = []
for _, r in items_sample.iterrows():
    seller = f"'{r['seller_id']}'" if r["seller_id"] else "NULL"
    all_item_rows.append(f"('{r['order_id']}', '{r['product_id']}', {int(r['order_item_id'])}, {seller}, {r['price']}, {r['freight_value']})")

for batch in chunks(all_item_rows, 100):
    lines.append("INSERT INTO order_items (order_id, product_id, order_item_id, seller_id, price, freight_value) VALUES")
    lines.append(",\n".join(batch) + ";")
lines.append("")

# Payments - par batch de 100
all_pay_rows = []
for _, r in payments_sample.iterrows():
    all_pay_rows.append(f"('{r['order_id']}', {int(r['payment_sequential'])}, '{r['payment_type']}', {int(r['payment_installments'])}, {r['payment_value']})")

for batch in chunks(all_pay_rows, 100):
    lines.append("INSERT INTO order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value) VALUES")
    lines.append(",\n".join(batch) + ";")
lines.append("")

# Requêtes SELECT
lines.append("""-- ============================================================
-- REQUÊTES SELECT
-- ============================================================

-- Requête 1 : CA par état
SELECT c.customer_state, COUNT(DISTINCT o.order_id) AS nb_commandes,
       ROUND(SUM(p.payment_value), 2) AS ca_total
FROM customers c
JOIN orders o         ON c.customer_id = o.customer_id
JOIN order_payments p ON o.order_id    = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state ORDER BY ca_total DESC;

-- Requête 2 : Top 5 catégories
SELECT pr.product_category, COUNT(oi.order_id) AS nb_ventes,
       ROUND(SUM(oi.price), 2) AS revenus
FROM products pr
JOIN order_items oi ON pr.product_id = oi.product_id
GROUP BY pr.product_category
HAVING nb_ventes >= 2
ORDER BY revenus DESC LIMIT 5;

-- Requête 3 : Clients multi-commandes
SELECT c.customer_id, c.customer_city, nb.total_commandes
FROM customers c
JOIN (
    SELECT customer_id, COUNT(*) AS total_commandes
    FROM orders WHERE order_status != 'canceled'
    GROUP BY customer_id HAVING total_commandes > 1
) AS nb ON c.customer_id = nb.customer_id
ORDER BY nb.total_commandes DESC;

-- Requête 4 : Jointure 3 tables
SELECT o.order_id, c.customer_city, c.customer_state,
       p.payment_type, ROUND(p.payment_value, 2) AS montant
FROM orders o
JOIN customers c       ON o.customer_id = c.customer_id
JOIN order_payments p  ON o.order_id    = p.order_id
WHERE o.order_status = 'delivered'
ORDER BY o.order_purchase_timestamp DESC;

-- Requête 5 : CTE paiements
WITH paiements_stats AS (
    SELECT payment_type, COUNT(*) AS nb,
           ROUND(AVG(payment_value), 2) AS moyenne
    FROM order_payments GROUP BY payment_type
)
SELECT * FROM paiements_stats ORDER BY moyenne DESC;""")

# Vérification
lines.append("""
SELECT 'customers' AS table_name, COUNT(*) AS nb_lignes FROM customers
UNION ALL SELECT 'products',       COUNT(*) FROM products
UNION ALL SELECT 'orders',         COUNT(*) FROM orders
UNION ALL SELECT 'order_items',    COUNT(*) FROM order_items
UNION ALL SELECT 'order_payments', COUNT(*) FROM order_payments;""")

# Écriture du fichier
output = "\n".join(lines)
with open("ecommerce_bdd.sql", "w", encoding="utf-8") as f:
    f.write(output)

print("✅ Fichier ecommerce_bdd.sql généré avec des données réelles !")
print("👉 Lance maintenant : mysql -u root -p < ecommerce_bdd.sql")