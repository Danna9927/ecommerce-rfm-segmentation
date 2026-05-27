-- ============================================================
--  PROJET FINAL - Algo & BDD
--  MSc2 Manager Data Marketing - INSEEC
--  Dataset : Olist Brazilian E-Commerce
--  Sujet   : Segmentation client RFM
-- ============================================================

DROP DATABASE IF EXISTS ecommerce_rfm;
CREATE DATABASE ecommerce_rfm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce_rfm;

-- ============================================================
-- PARTIE 1 : CRÉATION DES TABLES
-- ============================================================

-- Table customers
CREATE TABLE customers (
    customer_id     VARCHAR(50)  NOT NULL,
    customer_city   VARCHAR(100) NOT NULL,
    customer_state  VARCHAR(5)   NOT NULL,
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_customers PRIMARY KEY (customer_id)
);

-- Table products
CREATE TABLE products (
    product_id          VARCHAR(50)  NOT NULL,
    product_category    VARCHAR(100) NOT NULL,
    product_weight_g    DECIMAL(10,2),
    product_length_cm   DECIMAL(10,2),
    product_height_cm   DECIMAL(10,2),
    product_width_cm    DECIMAL(10,2),
    CONSTRAINT pk_products PRIMARY KEY (product_id)
);

-- Table orders
CREATE TABLE orders (
    order_id                    VARCHAR(50)  NOT NULL,
    customer_id                 VARCHAR(50)  NOT NULL,
    order_status                VARCHAR(30)  NOT NULL,
    order_purchase_timestamp    TIMESTAMP    NOT NULL,
    order_delivered_timestamp   TIMESTAMP    NULL,
    CONSTRAINT pk_orders        PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_cust   FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Table order_items  (relation many-to-many entre orders et products)
CREATE TABLE order_items (
    order_id        VARCHAR(50)    NOT NULL,
    product_id      VARCHAR(50)    NOT NULL,
    order_item_id   INT            NOT NULL,
    seller_id       VARCHAR(50),
    price           DECIMAL(10,2)  NOT NULL,
    freight_value   DECIMAL(10,2)  NOT NULL DEFAULT 0,
    CONSTRAINT pk_order_items      PRIMARY KEY (order_id, product_id, order_item_id),
    CONSTRAINT fk_items_order      FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    CONSTRAINT fk_items_product    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Table order_payments
CREATE TABLE order_payments (
    order_id            VARCHAR(50)   NOT NULL,
    payment_sequential  INT           NOT NULL,
    payment_type        VARCHAR(30)   NOT NULL,
    payment_installments INT          NOT NULL DEFAULT 1,
    payment_value       DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_payments     PRIMARY KEY (order_id, payment_sequential),
    CONSTRAINT fk_pay_order    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- Table rfm_segments  (remplie par le script Python)
CREATE TABLE rfm_segments (
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
);

-- ============================================================
-- PARTIE 2 : INSERTION DES DONNÉES (extrait Olist)
-- ============================================================

INSERT INTO customers (customer_id, customer_city, customer_state) VALUES
('c001', 'sao paulo',        'SP'),
('c002', 'rio de janeiro',   'RJ'),
('c003', 'belo horizonte',   'MG'),
('c004', 'curitiba',         'PR'),
('c005', 'porto alegre',     'RS'),
('c006', 'salvador',         'BA'),
('c007', 'fortaleza',        'CE'),
('c008', 'manaus',           'AM'),
('c009', 'recife',           'PE'),
('c010', 'brasilia',         'DF'),
('c011', 'sao paulo',        'SP'),
('c012', 'sao paulo',        'SP'),
('c013', 'rio de janeiro',   'RJ'),
('c014', 'curitiba',         'PR'),
('c015', 'belo horizonte',   'MG'),
('c016', 'porto alegre',     'RS'),
('c017', 'salvador',         'BA'),
('c018', 'fortaleza',        'CE'),
('c019', 'campinas',         'SP'),
('c020', 'goiania',          'GO'),
('c021', 'sao paulo',        'SP'),
('c022', 'rio de janeiro',   'RJ'),
('c023', 'natal',            'RN'),
('c024', 'maceio',           'AL'),
('c025', 'teresina',         'PI'),
('c026', 'campo grande',     'MS'),
('c027', 'joao pessoa',      'PB'),
('c028', 'aracaju',          'SE'),
('c029', 'cuiaba',           'MT'),
('c030', 'porto velho',      'RO'),
('c031', 'sao paulo',        'SP'),
('c032', 'rio de janeiro',   'RJ'),
('c033', 'belo horizonte',   'MG');

INSERT INTO products (product_id, product_category, product_weight_g, product_length_cm, product_height_cm, product_width_cm) VALUES
('p001', 'cama_mesa_banho',      800,  30, 10, 20),
('p002', 'esporte_lazer',        500,  25,  8, 15),
('p003', 'informatica_acessorios', 1200, 40, 15, 30),
('p004', 'beleza_saude',         300,  15,  5, 10),
('p005', 'moveis_decoracao',    5000,  60, 40, 50),
('p006', 'eletronicos',         2000,  35, 20, 25),
('p007', 'brinquedos',           400,  20,  8, 15),
('p008', 'ferramentas_jardim',  1500,  45, 20, 35),
('p009', 'alimentos',            600,  20, 10, 15),
('p010', 'livros',               350,  22,  3, 15),
('p011', 'automotivo',           900,  30, 10, 20),
('p012', 'moda_masculina',       250,  18,  5, 12),
('p013', 'moda_feminina',        220,  18,  5, 12),
('p014', 'perfumaria',           150,  10,  8,  8),
('p015', 'eletrodomesticos',    3500,  55, 35, 45);

INSERT INTO orders (order_id, customer_id, order_status, order_purchase_timestamp, order_delivered_timestamp) VALUES
('o001', 'c001', 'delivered',  '2024-01-05 10:00:00', '2024-01-12 15:00:00'),
('o002', 'c002', 'delivered',  '2024-01-08 11:30:00', '2024-01-15 14:00:00'),
('o003', 'c003', 'delivered',  '2024-01-10 09:00:00', '2024-01-18 16:00:00'),
('o004', 'c004', 'delivered',  '2024-01-15 14:00:00', '2024-01-22 10:00:00'),
('o005', 'c005', 'delivered',  '2024-01-20 16:00:00', '2024-01-28 12:00:00'),
('o006', 'c006', 'delivered',  '2024-02-01 10:00:00', '2024-02-09 15:00:00'),
('o007', 'c007', 'delivered',  '2024-02-05 13:00:00', '2024-02-13 11:00:00'),
('o008', 'c008', 'delivered',  '2024-02-10 09:30:00', '2024-02-19 14:00:00'),
('o009', 'c009', 'delivered',  '2024-02-14 15:00:00', '2024-02-22 10:00:00'),
('o010', 'c010', 'delivered',  '2024-02-20 11:00:00', '2024-02-28 16:00:00'),
('o011', 'c001', 'delivered',  '2024-03-01 10:00:00', '2024-03-09 14:00:00'),
('o012', 'c002', 'delivered',  '2024-03-05 12:00:00', '2024-03-14 11:00:00'),
('o013', 'c011', 'delivered',  '2024-03-10 09:00:00', '2024-03-18 15:00:00'),
('o014', 'c012', 'delivered',  '2024-03-15 14:00:00', '2024-03-23 10:00:00'),
('o015', 'c013', 'delivered',  '2024-03-20 16:00:00', '2024-03-29 12:00:00'),
('o016', 'c001', 'delivered',  '2024-04-01 10:00:00', '2024-04-10 15:00:00'),
('o017', 'c014', 'delivered',  '2024-04-05 11:00:00', '2024-04-14 14:00:00'),
('o018', 'c015', 'delivered',  '2024-04-10 13:00:00', '2024-04-19 11:00:00'),
('o019', 'c016', 'delivered',  '2024-04-15 09:00:00', '2024-04-24 16:00:00'),
('o020', 'c017', 'delivered',  '2024-04-20 15:00:00', '2024-04-29 10:00:00'),
('o021', 'c002', 'delivered',  '2024-05-01 10:00:00', '2024-05-10 14:00:00'),
('o022', 'c018', 'delivered',  '2024-05-05 12:00:00', '2024-05-14 11:00:00'),
('o023', 'c019', 'delivered',  '2024-05-10 09:00:00', '2024-05-19 15:00:00'),
('o024', 'c020', 'delivered',  '2024-05-15 14:00:00', '2024-05-24 10:00:00'),
('o025', 'c021', 'delivered',  '2024-05-20 16:00:00', '2024-05-29 12:00:00'),
('o026', 'c003', 'delivered',  '2024-06-01 10:00:00', '2024-06-10 15:00:00'),
('o027', 'c022', 'delivered',  '2024-06-05 11:00:00', '2024-06-14 14:00:00'),
('o028', 'c023', 'delivered',  '2024-06-10 13:00:00', '2024-06-19 11:00:00'),
('o029', 'c024', 'delivered',  '2024-06-15 09:00:00', '2024-06-24 16:00:00'),
('o030', 'c025', 'delivered',  '2024-06-20 15:00:00', '2024-06-29 10:00:00'),
('o031', 'c001', 'delivered',  '2024-07-01 10:00:00', '2024-07-10 14:00:00'),
('o032', 'c026', 'delivered',  '2024-07-05 12:00:00', '2024-07-14 11:00:00'),
('o033', 'c027', 'delivered',  '2024-07-10 09:00:00', '2024-07-19 15:00:00'),
('o034', 'c028', 'shipped',    '2024-07-15 14:00:00', NULL),
('o035', 'c029', 'shipped',    '2024-07-20 16:00:00', NULL),
('o036', 'c002', 'delivered',  '2024-08-01 10:00:00', '2024-08-10 15:00:00'),
('o037', 'c030', 'delivered',  '2024-08-05 11:00:00', '2024-08-14 14:00:00'),
('o038', 'c031', 'delivered',  '2024-08-10 13:00:00', '2024-08-19 11:00:00'),
('o039', 'c032', 'delivered',  '2024-08-15 09:00:00', '2024-08-24 16:00:00'),
('o040', 'c033', 'canceled',   '2024-08-20 15:00:00', NULL);

INSERT INTO order_items (order_id, product_id, order_item_id, seller_id, price, freight_value) VALUES
('o001','p001',1,'s001',  89.90, 12.50),
('o001','p004',2,'s002',  45.00,  8.00),
('o002','p006',1,'s003', 299.00, 25.00),
('o003','p003',1,'s004', 450.00, 30.00),
('o004','p002',1,'s005', 120.00, 15.00),
('o005','p005',1,'s006', 899.00, 80.00),
('o006','p007',1,'s007',  55.00, 10.00),
('o006','p010',2,'s008',  35.00,  5.00),
('o007','p008',1,'s009', 180.00, 20.00),
('o008','p009',1,'s010',  22.00,  6.00),
('o009','p011',1,'s001', 350.00, 28.00),
('o010','p012',1,'s002',  75.00, 12.00),
('o011','p006',1,'s003', 320.00, 25.00),
('o011','p014',2,'s004',  90.00, 10.00),
('o012','p013',1,'s005',  68.00, 10.00),
('o013','p001',1,'s006',  95.00, 12.50),
('o014','p015',1,'s007',1299.00,100.00),
('o015','p004',1,'s008',  48.00,  8.00),
('o016','p003',1,'s009', 480.00, 30.00),
('o017','p002',1,'s010', 135.00, 15.00),
('o017','p007',2,'s001',  60.00, 10.00),
('o018','p010',1,'s002',  38.00,  5.00),
('o019','p006',1,'s003', 280.00, 25.00),
('o020','p005',1,'s004', 950.00, 80.00),
('o021','p001',1,'s005',  85.00, 12.50),
('o021','p004',2,'s006',  42.00,  8.00),
('o021','p012',3,'s007',  70.00, 12.00),
('o022','p008',1,'s008', 195.00, 20.00),
('o023','p009',1,'s009',  25.00,  6.00),
('o024','p011',1,'s010', 370.00, 28.00),
('o025','p013',1,'s001',  72.00, 10.00),
('o026','p006',1,'s002', 310.00, 25.00),
('o027','p015',1,'s003',1350.00,100.00),
('o028','p007',1,'s004',  58.00, 10.00),
('o029','p010',1,'s005',  32.00,  5.00),
('o030','p003',1,'s006', 465.00, 30.00),
('o031','p001',1,'s007',  92.00, 12.50),
('o031','p006',2,'s008', 295.00, 25.00),
('o032','p005',1,'s009', 870.00, 80.00),
('o033','p002',1,'s010', 125.00, 15.00),
('o034','p004',1,'s001',  50.00,  8.00),
('o035','p012',1,'s002',  80.00, 12.00),
('o036','p001',1,'s003',  88.00, 12.50),
('o036','p011',2,'s004', 340.00, 28.00),
('o037','p014',1,'s005',  95.00, 10.00),
('o038','p009',1,'s006',  20.00,  6.00),
('o039','p013',1,'s007',  65.00, 10.00),
('o040','p008',1,'s008', 200.00, 20.00);

INSERT INTO order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value) VALUES
('o001',1,'credit_card',3,  150.40),
('o002',1,'credit_card',6,  324.00),
('o003',1,'boleto',    1,  480.00),
('o004',1,'credit_card',2,  135.00),
('o005',1,'credit_card',12, 979.00),
('o006',1,'debit_card', 1,  105.00),
('o007',1,'credit_card',3,  200.00),
('o008',1,'boleto',    1,   28.00),
('o009',1,'credit_card',6,  378.00),
('o010',1,'credit_card',2,   87.00),
('o011',1,'credit_card',3,  435.00),
('o012',1,'debit_card', 1,   78.00),
('o013',1,'credit_card',1,  107.50),
('o014',1,'credit_card',12,1399.00),
('o015',1,'boleto',    1,   56.00),
('o016',1,'credit_card',6,  510.00),
('o017',1,'credit_card',3,  220.00),
('o018',1,'debit_card', 1,   43.00),
('o019',1,'credit_card',3,  305.00),
('o020',1,'credit_card',12,1030.00),
('o021',1,'credit_card',3,  217.50),
('o022',1,'boleto',    1,  215.00),
('o023',1,'debit_card', 1,   31.00),
('o024',1,'credit_card',6,  398.00),
('o025',1,'credit_card',2,   82.00),
('o026',1,'credit_card',3,  335.00),
('o027',1,'credit_card',12,1450.00),
('o028',1,'boleto',    1,   68.00),
('o029',1,'debit_card', 1,   37.00),
('o030',1,'credit_card',6,  495.00),
('o031',1,'credit_card',3,  424.50),
('o032',1,'credit_card',12, 950.00),
('o033',1,'credit_card',2,  140.00),
('o034',1,'boleto',    1,   58.00),
('o035',1,'credit_card',1,   92.00),
('o036',1,'credit_card',3,  460.50),
('o037',1,'debit_card', 1,  105.00),
('o038',1,'boleto',    1,   26.00),
('o039',1,'credit_card',2,   75.00),
('o040',1,'credit_card',1,  220.00);

-- ============================================================
-- PARTIE 3 : REQUÊTES SELECT (5 requêtes variées)
-- ============================================================

-- Requête 1 : Chiffre d'affaires total par état (WHERE + GROUP BY + ORDER BY)
SELECT
    c.customer_state                        AS etat,
    COUNT(DISTINCT o.order_id)              AS nb_commandes,
    ROUND(SUM(p.payment_value), 2)          AS ca_total,
    ROUND(AVG(p.payment_value), 2)          AS panier_moyen
FROM customers c
JOIN orders o        ON c.customer_id = o.customer_id
JOIN order_payments p ON o.order_id   = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY ca_total DESC;

-- Requête 2 : Top 5 catégories de produits par revenus (GROUP BY + HAVING + LIMIT)
SELECT
    pr.product_category                     AS categorie,
    COUNT(oi.order_id)                      AS nb_ventes,
    ROUND(SUM(oi.price), 2)                 AS revenus_totaux,
    ROUND(AVG(oi.price), 2)                 AS prix_moyen
FROM products pr
JOIN order_items oi ON pr.product_id = oi.product_id
GROUP BY pr.product_category
HAVING nb_ventes >= 2
ORDER BY revenus_totaux DESC
LIMIT 5;

-- Requête 3 : Clients avec plusieurs commandes (sous-requête)
SELECT
    c.customer_id,
    c.customer_city,
    c.customer_state,
    nb.total_commandes
FROM customers c
JOIN (
    SELECT customer_id, COUNT(*) AS total_commandes
    FROM orders
    WHERE order_status != 'canceled'
    GROUP BY customer_id
    HAVING total_commandes > 1
) AS nb ON c.customer_id = nb.customer_id
ORDER BY nb.total_commandes DESC;

-- Requête 4 : Jointure sur 3 tables — détail des commandes avec paiement
SELECT
    o.order_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    p.payment_type,
    p.payment_installments,
    ROUND(p.payment_value, 2)               AS montant_paye
FROM orders o
JOIN customers c       ON o.customer_id = c.customer_id
JOIN order_payments p  ON o.order_id   = p.order_id
WHERE o.order_status IN ('delivered', 'shipped')
ORDER BY o.order_purchase_timestamp DESC;

-- Requête 5 : CTE — panier moyen par mode de paiement
WITH paiements_stats AS (
    SELECT
        payment_type,
        COUNT(*)                            AS nb_transactions,
        ROUND(SUM(payment_value), 2)        AS total,
        ROUND(AVG(payment_value), 2)        AS moyenne,
        ROUND(MIN(payment_value), 2)        AS minimum,
        ROUND(MAX(payment_value), 2)        AS maximum
    FROM order_payments
    GROUP BY payment_type
)
SELECT *
FROM paiements_stats
ORDER BY total DESC;

-- ============================================================
-- PARTIE 4 : VUE
-- ============================================================

CREATE OR REPLACE VIEW vue_client_resume AS
SELECT
    c.customer_id,
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT o.order_id)              AS nb_commandes,
    ROUND(SUM(p.payment_value), 2)          AS ca_client,
    ROUND(AVG(p.payment_value), 2)          AS panier_moyen,
    MAX(o.order_purchase_timestamp)         AS derniere_commande,
    DATEDIFF(CURDATE(), MAX(o.order_purchase_timestamp)) AS jours_depuis_achat
FROM customers c
LEFT JOIN orders o        ON c.customer_id  = o.customer_id
LEFT JOIN order_payments p ON o.order_id   = p.order_id
WHERE o.order_status != 'canceled' OR o.order_status IS NULL
GROUP BY c.customer_id, c.customer_city, c.customer_state;

-- ============================================================
-- PARTIE 5 : PROCÉDURE STOCKÉE
-- ============================================================

DELIMITER $$

CREATE PROCEDURE GetTopClients(IN p_limit INT, IN p_state VARCHAR(5))
BEGIN
    -- Retourne les meilleurs clients par CA pour un état donné
    SELECT
        c.customer_id,
        c.customer_city,
        c.customer_state,
        COUNT(DISTINCT o.order_id)          AS nb_commandes,
        ROUND(SUM(p.payment_value), 2)      AS ca_total
    FROM customers c
    JOIN orders o        ON c.customer_id = o.customer_id
    JOIN order_payments p ON o.order_id   = p.order_id
    WHERE o.order_status = 'delivered'
      AND (p_state IS NULL OR c.customer_state = p_state)
    GROUP BY c.customer_id, c.customer_city, c.customer_state
    ORDER BY ca_total DESC
    LIMIT p_limit;
END$$

DELIMITER ;

-- Exemples d'appel :
-- CALL GetTopClients(10, NULL);    -- top 10 tous états
-- CALL GetTopClients(5,  'SP');    -- top 5 état SP

-- ============================================================
-- VÉRIFICATION RAPIDE
-- ============================================================

SELECT 'customers'      AS table_name, COUNT(*) AS nb_lignes FROM customers
UNION ALL
SELECT 'products',       COUNT(*) FROM products
UNION ALL
SELECT 'orders',         COUNT(*) FROM orders
UNION ALL
SELECT 'order_items',    COUNT(*) FROM order_items
UNION ALL
SELECT 'order_payments', COUNT(*) FROM order_payments;
