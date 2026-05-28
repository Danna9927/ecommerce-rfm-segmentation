# 🛒 Segmentation Client RFM — E-Commerce Olist

> Projet Final — Algo & Bases de Données  
> MSc2 Manager Data Marketing — INSEEC 2026

## 📌 Problématique

Comment identifier et cibler les différents segments de clients
(Champions, Loyaux, Dormants, Nouveaux) pour optimiser les campagnes
marketing d'une plateforme e-commerce brésilienne ?

## 🗂️ Dataset

- **Source** : [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Volume** : 200 clients, 200 commandes, 204 produits, 236 articles
- **Période** : 2016 — 2018

## 🏗️ Architecture du projet

## 🗄️ Modélisation de la base de données

### Schéma (6 tables)

- **customers** : clients avec ville et état
- **products** : catalogue produits par catégorie
- **orders** : commandes avec statut et dates
- **order_items** : détail des articles (many-to-many orders ↔ products)
- **order_payments** : paiements par commande
- **rfm_segments** : résultats de la segmentation RFM (générée par Python)

### Contraintes techniques
- FOREIGN KEY sur toutes les relations
- NOT NULL sur les champs critiques
- Many-to-many : orders ↔ products via order_items
- 1 Vue : `vue_client_resume`
- 1 Procédure stockée : `GetTopClients(limit, state)`
- 5 requêtes SELECT avec WHERE, GROUP BY, HAVING, ORDER BY, LIMIT, CTE, sous-requête, jointure 3 tables

## 🐍 Pipeline Python

1. **Connexion MySQL** via `mysql-connector-python` + `.env`
2. **Chargement** des données avec `pandas`
3. **API externe** : [exchangerate-api.com](https://api.exchangerate-api.com) pour convertir BRL → EUR
4. **Algorithme RFM** :
   - R (Récence) : jours depuis le dernier achat
   - F (Fréquence) : nombre de commandes distinctes
   - M (Montant) : total dépensé
   - Scoring par quartiles (1-4) → score global (3-12)
   - Date de référence RFM : Octobre 2018
5. **Segmentation** : Champions / Loyal / Potentiel / Nouveaux clients / Dormants / A risque
6. **Écriture** des résultats dans la table `rfm_segments`

## 📊 Dashboard Plotly

Lancé avec `py dashboard.py` → accessible sur `http://127.0.0.1:8050`

### KPIs affichés
- Nombre de clients analysés
- CA total (BRL)
- Panier moyen (BRL)
- Récence moyenne (jours)

### Graphiques
- Donut chart — répartition des segments
- Bar chart — CA moyen par segment
- Line chart — évolution du CA mensuel
- Pie chart — modes de paiement
- Scatter plot — Récence vs Montant par segment

### Filtres interactifs
- Dropdown : filtre par segment client
- Dropdown : filtre par état (région)
- Slider : score RFM minimum

## ▶️ Installation et lancement

### 1. Cloner le repo
```bash
git clone https://github.com/Danna9927/TON_REPO.git
cd TON_REPO
```

### 2. Installer les dépendances
```bash
py -m pip install mysql-connector-python pandas requests python-dotenv dash plotly
```

### 3. Configurer la base de données
```bash
# Exécuter le fichier SQL dans MySQL
mysql -u root -p < ecommerce_bdd.sql
```

### 4. Configurer les variables d'environnement
```bash
# Créer un fichier .env à la racine
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=ton_mot_de_passe
DB_NAME=ecommerce_rfm
```

### 5. Lancer le pipeline RFM
```bash
py rfm_pipeline.py
```

### 6. Lancer le dashboard
```bash
py dashboard.py
```

## 🔒 Sécurité

Le fichier `.env` contenant les credentials MySQL n'est **jamais commité**.  
Il est listé dans `.gitignore`.

## 🛠️ Stack technique

| Outil | Usage |
|---|---|
| MySQL 8 | Base de données relationnelle |
| Python 3.12 | Pipeline de données |
| Pandas | Manipulation des données |
| Plotly Dash | Dashboard interactif |
| exchangerate-api | Taux de change BRL→EUR |
| VSCode | Environnement de développement |