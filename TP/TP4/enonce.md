## 🧩 **Vue d’ensemble du projet**

Ce projet met en place un **pipeline de traitement de données e-commerce** automatisé à l’aide de **conteneurs Python** et de **MinIO** (équivalent S3).
Il simule les **trois couches d’un Data Lakehouse** :

| Couche        | Rôle principal               | Description                                                                                                        |
| :------------ | :--------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| 🟤 **Bronze** | Données brutes               | Données générées automatiquement par le simulateur (clients, commandes, clics). Non nettoyées, parfois corrompues. |
| ⚪ **Silver**  | Données nettoyées            | Données corrigées, standardisées et anonymisées. Exploitables pour les traitements.                                |
| 🟡 **Gold**   | Données enrichies / agrégées | Données agrégées sous forme de KPI marketing et business, prêtes pour la visualisation et l’analyse.               |

---

## 🚀 **Fonctionnement global**

Trois conteneurs Python fonctionnent en parallèle toutes les 5 secondes :

| Conteneur       | Fonction                                | Source     | Cible             |
| :-------------- | :-------------------------------------- | :--------- | :---------------- |
| 🧱 `generator`  | Génère les données brutes (bronze)      | —          | Bucket **bronze** |
| 🧼 `cleaner`    | Nettoie et anonymise les données        | **bronze** | Bucket **silver** |
| 📊 `aggregator` | Agrège et calcule des indicateurs (KPI) | **silver** | Bucket **gold**   |

---

## 🟤 **Bronze — Données brutes**

Le service **`generator`** simule les activités d’un site e-commerce.

### Types de fichiers envoyés

| Fichier           | Format     | Contenu                                                                                             | Exemple de corruption                                               |
| :---------------- | :--------- | :-------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------ |
| `customers_*.csv` | CSV        | Informations clients : id, prénom, nom, email, pays, date d’inscription                             | emails manquants, dates invalides (`32/13/2025`)                    |
| `orders_*.json`   | JSON       | Commandes : id, client, produit, quantité, prix, total, timestamp, canal (`web`, `mobile`, `store`) | quantités négatives, totaux manquants, timestamp invalide, doublons |
| `clicks_*.txt`    | JSON Lines | Traces de navigation : id client, page visitée, IP, timestamp                                       | IP invalides (`999.999.999.999`)                                    |

⏱ Ces fichiers sont produits toutes les **5 secondes** et poussés dans le **bucket MinIO “bronze”**.

---

## ⚪ **Silver — Données nettoyées & anonymisées**

Le service **`cleaner`** lit le bucket **bronze/** toutes les 5 secondes et applique un **nettoyage complet** avant d’écrire dans **silver/** au format CSV.

### Nettoyage effectué

#### 🧍‍♂️ Customers

* Conversion du champ `signup_date` en date (suppression des lignes invalides)
* Remplissage du pays manquant par `"NA"`
* Suppression des lignes sans `customer_id`
* **Anonymisation :**

  * `email` remplacé par son **hash SHA-256** tronqué (`email_h`)
  * conservation uniquement des initiales (`first_initial`, `last_initial`)
* Suppression des champs sensibles (`first_name`, `last_name`, `email`)

#### 🧾 Orders

* Conversion en numériques (`quantity`, `unit_price`, `total_amount`)
* Correction des valeurs négatives (mise à 0 ou recalcul)
* Recalcul du `total_amount` quand il est manquant
* Correction des dates (`order_ts`)
* Suppression des commandes invalides (date, id manquant)
* Suppression des doublons sur `order_id` (garde la plus récente)

#### 🖱 Clicks

* Lecture des lignes JSON (une par ligne)
* Validation du champ `ip` (regex IPv4)
* Suppression des lignes invalides
* Suppression du champ `ip` (anonymisation)
* Conversion des timestamps (`ts`) en datetime

✅ Résultat :

* `customers_clean_*.csv`
* `orders_clean_*.csv`
* `clicks_clean_*.csv`

---

## 🟡 **Gold — Données agrégées et KPI**

Le service **`aggregator`** lit régulièrement le **bucket silver/** pour générer des **indicateurs d’analyse** destinés aux équipes marketing, comptabilité et contrôle de gestion.

### Calculs effectués

| KPI                              | Description                                                               | Source                                     |
| :------------------------------- | :------------------------------------------------------------------------ | :----------------------------------------- |
| 📈 **Sales by day**              | Chiffre d’affaires agrégé par jour (`SUM(total_amount)` par `order_date`) | `orders_clean.csv`                         |
| 🏆 **Top products**              | Produits les plus vendus (top 10 par total CA)                            | `orders_clean.csv`                         |
| 💰 **AOV (Average Order Value)** | Panier moyen par commande                                                 | `orders_clean.csv`                         |
| 📱 **Revenue by channel**        | CA par canal (`web`, `mobile`, `store`)                                   | `orders_clean.csv`                         |
| 🌍 **Revenue by country**        | CA par pays (jointure avec `customers_clean.csv`)                         | `orders_clean.csv` + `customers_clean.csv` |

### Fichiers enregistrés dans Gold

Chaque indicateur est stocké en **CSV** (daté avec timestamp) :

```
gold/
 ├── sales_by_day/sales_by_day_20251113T103500.csv
 ├── top_products/top_products_20251113T103500.csv
 ├── aov/aov_20251113T103500.csv
 ├── revenue_by_channel/revenue_by_channel_20251113T103500.csv
 └── revenue_by_country/revenue_by_country_20251113T103500.csv
```

Chaque fichier contient des données prêtes à être consommées par :

* un **outil BI** (Metabase, Power BI, Grafana)
* ou un **dashboard CSV viewer** simple.

---

## 📊 **Résumé synthétique**

| Étape      | Bucket    | Format         | Action principale                            | Exemple de sortie           |
| :--------- | :-------- | :------------- | :------------------------------------------- | :-------------------------- |
| **Bronze** | `bronze/` | CSV, JSON, TXT | Génération brute (clients, commandes, clics) | `customers_20251113.csv`    |
| **Silver** | `silver/` | CSV            | Nettoyage, typage, anonymisation             | `orders_clean_20251113.csv` |
| **Gold**   | `gold/`   | CSV            | Calculs de KPI (CA, top produits, AOV, etc.) | `sales_by_day_20251113.csv` |

