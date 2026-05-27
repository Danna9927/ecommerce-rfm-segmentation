# ============================================================
#  PROJET FINAL - Algo & BDD
#  MSc2 Manager Data Marketing - INSEEC
#  Script : Dashboard Plotly - Segmentation RFM
# ============================================================

import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

load_dotenv()

# ============================================================
# 1. CONNEXION ET CHARGEMENT DES DONNÉES
# ============================================================

def get_connection():
    return mysql.connector.connect(
        host     = os.getenv("DB_HOST",     "127.0.0.1"),
        port     = int(os.getenv("DB_PORT", "3306")),
        user     = os.getenv("DB_USER",     "root"),
        password = os.getenv("DB_PASSWORD", ""),
        database = os.getenv("DB_NAME",     "ecommerce_rfm")
    )

def load_all_data():
    conn = get_connection()

    rfm = pd.read_sql("""
        SELECT r.*, c.customer_city, c.customer_state
        FROM rfm_segments r
        JOIN customers c ON r.customer_id = c.customer_id
    """, conn)

    orders = pd.read_sql("""
        SELECT o.order_id, o.order_purchase_timestamp,
               o.order_status, c.customer_state,
               p.payment_value, p.payment_type
        FROM orders o
        JOIN customers c       ON o.customer_id = c.customer_id
        JOIN order_payments p  ON o.order_id    = p.order_id
        WHERE o.order_status != 'canceled'
    """, conn)

    conn.close()
    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
    orders["month"] = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)
    return rfm, orders

rfm_df, orders_df = load_all_data()

# ============================================================
# 2. INITIALISATION DE L'APP DASH
# ============================================================

app = Dash(__name__)
app.title = "Dashboard RFM - E-Commerce"

SEGMENTS    = ["Tous"] + sorted(rfm_df["segment"].unique().tolist())
STATES      = ["Tous"] + sorted(rfm_df["customer_state"].unique().tolist())
COLORS      = {
    "Champions"       : "#534AB7",
    "Loyal"           : "#1D9E75",
    "Potentiel"       : "#EF9F27",
    "Nouveaux clients": "#378ADD",
    "Dormants"        : "#888780",
    "A risque"        : "#E24B4A",
}

# ============================================================
# 3. LAYOUT DU DASHBOARD
# ============================================================

app.layout = html.Div(style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#f5f5f5", "minHeight": "100vh", "padding": "20px"}, children=[

    # Header
    html.Div(style={"backgroundColor": "#534AB7", "padding": "20px 30px", "borderRadius": "12px", "marginBottom": "20px"}, children=[
        html.H1("Dashboard Segmentation RFM", style={"color": "white", "margin": 0, "fontSize": "24px"}),
        html.P("MSc2 Manager Data Marketing — Olist Brazilian E-Commerce", style={"color": "#CECBF6", "margin": "4px 0 0", "fontSize": "13px"}),
    ]),

    # Filtres
    html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "20px", "flexWrap": "wrap"}, children=[
        html.Div([
            html.Label("Segment client", style={"fontSize": "13px", "color": "#555", "marginBottom": "6px", "display": "block"}),
            dcc.Dropdown(id="filter-segment", options=[{"label": s, "value": s} for s in SEGMENTS], value="Tous", clearable=False, style={"width": "220px"}),
        ]),
        html.Div([
            html.Label("État (région)", style={"fontSize": "13px", "color": "#555", "marginBottom": "6px", "display": "block"}),
            dcc.Dropdown(id="filter-state", options=[{"label": s, "value": s} for s in STATES], value="Tous", clearable=False, style={"width": "180px"}),
        ]),
        html.Div([
            html.Label("Score RFM minimum", style={"fontSize": "13px", "color": "#555", "marginBottom": "6px", "display": "block"}),
            dcc.Slider(id="filter-score", min=3, max=12, step=1, value=3,
                marks={i: str(i) for i in range(3, 13)},
                tooltip={"placement": "bottom", "always_visible": False}),
        ], style={"flex": "1", "minWidth": "250px"}),
    ]),

    # KPIs
    html.Div(id="kpi-cards", style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "16px", "marginBottom": "20px"}),

    # Graphiques ligne 1
    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"}, children=[
        html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "20px"}, children=[
            html.H3("Répartition des segments", style={"margin": "0 0 16px", "fontSize": "15px", "color": "#333"}),
            dcc.Graph(id="chart-segments", config={"displayModeBar": False}),
        ]),
        html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "20px"}, children=[
            html.H3("CA moyen par segment (€)", style={"margin": "0 0 16px", "fontSize": "15px", "color": "#333"}),
            dcc.Graph(id="chart-ca", config={"displayModeBar": False}),
        ]),
    ]),

    # Graphiques ligne 2
    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"}, children=[
        html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "20px"}, children=[
            html.H3("Évolution du CA mensuel (BRL)", style={"margin": "0 0 16px", "fontSize": "15px", "color": "#333"}),
            dcc.Graph(id="chart-monthly", config={"displayModeBar": False}),
        ]),
        html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "20px"}, children=[
            html.H3("Modes de paiement", style={"margin": "0 0 16px", "fontSize": "15px", "color": "#333"}),
            dcc.Graph(id="chart-payment", config={"displayModeBar": False}),
        ]),
    ]),

    # Scatter RFM
    html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "20px", "marginBottom": "16px"}, children=[
        html.H3("Carte RFM — Récence vs Montant", style={"margin": "0 0 16px", "fontSize": "15px", "color": "#333"}),
        dcc.Graph(id="chart-scatter", config={"displayModeBar": False}),
    ]),
])

# ============================================================
# 4. CALLBACKS
# ============================================================

@app.callback(
    Output("kpi-cards",     "children"),
    Output("chart-segments","figure"),
    Output("chart-ca",      "figure"),
    Output("chart-monthly", "figure"),
    Output("chart-payment", "figure"),
    Output("chart-scatter", "figure"),
    Input("filter-segment", "value"),
    Input("filter-state",   "value"),
    Input("filter-score",   "value"),
)
def update_dashboard(segment, state, min_score):

    # Filtrage RFM
    df = rfm_df.copy()
    if segment != "Tous":
        df = df[df["segment"] == segment]
    if state != "Tous":
        df = df[df["customer_state"] == state]
    df = df[df["rfm_score"] >= min_score]

    # ── KPIs ──────────────────────────────────────────────
    nb_clients   = len(df)
    ca_total     = df["monetary"].sum()
    panier_moy   = df["monetary"].mean() if nb_clients > 0 else 0
    recence_moy  = df["recency_days"].mean() if nb_clients > 0 else 0

    def kpi_card(label, value, color):
        return html.Div(style={
            "backgroundColor": "white", "borderRadius": "10px",
            "padding": "16px 20px", "borderTop": f"4px solid {color}"
        }, children=[
            html.P(label, style={"fontSize": "12px", "color": "#888", "margin": "0 0 6px"}),
            html.P(value, style={"fontSize": "22px", "fontWeight": "600", "color": "#333", "margin": 0}),
        ])

    kpis = [
        kpi_card("Clients analysés",   f"{nb_clients}",            "#534AB7"),
        kpi_card("CA total (BRL)",      f"R$ {ca_total:,.0f}",      "#1D9E75"),
        kpi_card("Panier moyen (BRL)",  f"R$ {panier_moy:,.0f}",    "#EF9F27"),
        kpi_card("Récence moyenne",     f"{recence_moy:.0f} jours", "#378ADD"),
    ]

    # ── Graphique 1 : Donut segments ──────────────────────
    seg_counts = df["segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]
    fig_seg = px.pie(seg_counts, names="segment", values="count",
                     hole=0.5, color="segment",
                     color_discrete_map=COLORS)
    fig_seg.update_traces(textposition="outside", textinfo="percent+label")
    fig_seg.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=260)

    # ── Graphique 2 : CA moyen par segment ────────────────
    ca_seg = df.groupby("segment")["monetary"].mean().reset_index()
    ca_seg.columns = ["segment", "ca_moyen"]
    ca_seg = ca_seg.sort_values("ca_moyen", ascending=True)
    fig_ca = px.bar(ca_seg, x="ca_moyen", y="segment", orientation="h",
                    color="segment", color_discrete_map=COLORS,
                    labels={"ca_moyen": "CA moyen (BRL)", "segment": ""})
    fig_ca.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=260)

    # ── Graphique 3 : CA mensuel ──────────────────────────
    monthly = orders_df.groupby("month")["payment_value"].sum().reset_index()
    fig_monthly = px.line(monthly, x="month", y="payment_value",
                          markers=True, color_discrete_sequence=["#534AB7"],
                          labels={"month": "Mois", "payment_value": "CA (BRL)"})
    fig_monthly.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=260)

    # ── Graphique 4 : Modes de paiement ───────────────────
    pay = orders_df["payment_type"].value_counts().reset_index()
    pay.columns = ["type", "count"]
    fig_pay = px.pie(pay, names="type", values="count", hole=0.4,
                     color_discrete_sequence=["#534AB7","#1D9E75","#EF9F27","#378ADD"])
    fig_pay.update_traces(textposition="outside", textinfo="percent+label")
    fig_pay.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=260)

    # ── Graphique 5 : Scatter RFM ─────────────────────────
    fig_scatter = px.scatter(df, x="recency_days", y="monetary",
                             color="segment", size="frequency",
                             color_discrete_map=COLORS,
                             hover_data=["customer_id", "rfm_score"],
                             labels={"recency_days": "Récence (jours)", "monetary": "Montant total (BRL)", "segment": "Segment"})
    fig_scatter.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320)

    return kpis, fig_seg, fig_ca, fig_monthly, fig_pay, fig_scatter


# ============================================================
# 5. LANCEMENT
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)