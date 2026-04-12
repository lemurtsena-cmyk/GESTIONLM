import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

DB = "gestion_tables_mga.db"

# ================================================================
# CONFIGURATION
# ================================================================
st.set_page_config(
    page_title="Melamine & Metallique",
    layout="wide",
    page_icon="🏗️",
    initial_sidebar_state="expanded"
)

# ================================================================
# CSS MODE SOMBRE COMPLET
# ================================================================
st.markdown("""
<style>
/* ==================== IMPORTS ==================== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ==================== GLOBAL ==================== */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #0a0f1c;
    color: #e2e8f0;
}

/* ==================== SCROLLBAR ==================== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #111827;
}
::-webkit-scrollbar-thumb {
    background: #475569;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: #7b68ee;
}

/* ==================== SIDEBAR ==================== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1629 0%, #111d35 50%, #0d1a30 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-size: 0.95rem;
    padding: 6px 12px;
    border-radius: 8px;
    transition: all 0.25s ease;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: #c4b5fd !important;
    background: rgba(123, 104, 238, 0.08);
}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"] {
    margin-bottom: 2px;
}

/* ==================== LOGO SIDEBAR ==================== */
.sidebar-logo {
    text-align: center;
    padding: 24px 10px 16px 10px;
}
.sidebar-logo h2 {
    background: linear-gradient(135deg, #a78bfa, #c4b5fd, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.5rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}
.sidebar-logo p {
    color: rgba(148, 163, 184, 0.6) !important;
    font-size: 0.75rem;
    margin-top: 6px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ==================== SIDEBAR MINI STATS ==================== */
.sidebar-stats {
    padding: 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    margin: 8px 0;
}
.sidebar-stats .stats-title {
    color: rgba(148,163,184,0.6) !important;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}
.sidebar-stats .stats-row {
    display: flex;
    justify-content: space-around;
}
.sidebar-stats .stat-item {
    text-align: center;
}
.sidebar-stats .stat-number {
    font-size: 1.5rem;
    font-weight: 700;
}
.sidebar-stats .stat-label {
    color: rgba(148,163,184,0.5) !important;
    font-size: 0.7rem;
    margin-top: 2px;
}

/* ==================== TITRES ==================== */
h1 {
    background: linear-gradient(135deg, #a78bfa, #818cf8) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    font-weight: 800 !important;
}
h2, h3 {
    color: #c4d0ff !important;
    font-weight: 700 !important;
}

/* ==================== PAGE HEADER ==================== */
.page-header {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 12px 0 24px 0;
    border-bottom: 2px solid rgba(123, 104, 238, 0.3);
    margin-bottom: 28px;
}
.page-header .icon {
    font-size: 2.4rem;
    line-height: 1;
}
.page-header .title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}
.page-header .subtitle {
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 4px;
}

/* ==================== MÉTRIQUES ==================== */
div[data-testid="stMetric"] {
    border-radius: 16px;
    padding: 22px 24px;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 44px rgba(0, 0, 0, 0.5);
}
div[data-testid="stMetric"] label {
    color: rgba(148, 163, 184, 0.85) !important;
    font-weight: 500;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-weight: 700;
    font-size: 1.55rem !important;
}

/* Métrique 1 — Violet */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #312e81, #4c1d95);
    border-color: rgba(139, 92, 246, 0.3);
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #c4b5fd !important;
}

/* Métrique 2 — Vert */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border-color: rgba(52, 211, 153, 0.3);
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #6ee7b7 !important;
}

/* Métrique 3 — Bleu/Rose */
div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e1b4b, #581c87);
    border-color: rgba(192, 132, 252, 0.3);
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #e9d5ff !important;
}

/* ==================== CARTES CUSTOM ==================== */
.custom-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px 24px;
    color: #e2e8f0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    margin-bottom: 16px;
}

/* ==================== MINI STATS ==================== */
.stat-mini {
    text-align: center;
    padding: 16px 12px;
    border-radius: 14px;
    background: #111827;
    border: 1px solid rgba(255,255,255,0.06);
}
.stat-mini .number {
    font-size: 1.9rem;
    font-weight: 800;
    color: #a78bfa;
}
.stat-mini .label {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* ==================== INPUTS ==================== */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #1e2937 !important;
    color: #e2e8f0 !important;
    border: 1.5px solid #334155 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #7b68ee !important;
    box-shadow: 0 0 0 3px rgba(123, 104, 238, 0.2) !important;
}
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stDateInput label, .stRadio label {
    color: #94a3b8 !important;
    font-weight: 500;
}

/* Select */
.stSelectbox > div > div {
    background: #1e2937 !important;
    border: 1.5px solid #334155 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ==================== BOUTONS ==================== */
.stButton > button {
    border-radius: 10px !important;
    padding: 0.55rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
    border: none !important;
    background: linear-gradient(135deg, #7b68ee, #a78bfa) !important;
    color: white !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(123, 104, 238, 0.4) !important;
}

.stFormSubmitButton > button {
    background: linear-gradient(135deg, #7b68ee 0%, #a78bfa 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.65rem 2rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem;
    width: 100%;
    transition: all 0.3s ease;
    letter-spacing: 0.3px;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(123, 104, 238, 0.45) !important;
}

/* ==================== TABS ==================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #111827;
    border-radius: 14px;
    padding: 5px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 500;
    color: #94a3b8 !important;
    transition: all 0.25s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #c4b5fd !important;
    background: rgba(123, 104, 238, 0.08);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7b68ee, #a78bfa) !important;
    color: white !important;
    font-weight: 600;
}

/* ==================== DATAFRAME ==================== */
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}

/* ==================== EXPANDER ==================== */
.streamlit-expanderHeader {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px !important;
    font-weight: 600;
    color: #c4d0ff !important;
}

/* ==================== ALERTES ==================== */
.stAlert {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.06);
}

/* ==================== DIVIDER ==================== */
hr {
    border-color: rgba(255,255,255,0.06) !important;
}

/* ==================== BADGES STOCK ==================== */
.stock-ok {
    background: rgba(34, 197, 94, 0.15);
    color: #86efac;
    padding: 5px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid rgba(34, 197, 94, 0.2);
}
.stock-low {
    background: rgba(234, 179, 8, 0.15);
    color: #fde047;
    padding: 5px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid rgba(234, 179, 8, 0.2);
}
.stock-out {
    background: rgba(239, 68, 68, 0.15);
    color: #fca5a5;
    padding: 5px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid rgba(239, 68, 68, 0.2);
}

/* ==================== ALERTES STOCK SIDEBAR ==================== */
.alert-card {
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-size: 0.85rem;
    border: 1px solid rgba(255,255,255,0.06);
}
.alert-card.danger {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.2);
}
.alert-card.warning {
    background: rgba(234, 179, 8, 0.1);
    border-color: rgba(234, 179, 8, 0.2);
}
.alert-card.success {
    background: rgba(34, 197, 94, 0.1);
    border-color: rgba(34, 197, 94, 0.2);
}

/* ==================== PROGRESS BARS ==================== */
.progress-bar-bg {
    background: #1e2937;
    border-radius: 10px;
    height: 8px;
    overflow: hidden;
    margin-top: 6px;
}
.progress-bar-fill {
    background: linear-gradient(90deg, #7b68ee, #a78bfa);
    height: 100%;
    border-radius: 10px;
    transition: width 0.5s ease;
}

/* ==================== DOWNLOAD BUTTON ==================== */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1e2937, #334155) !important;
    border: 1px solid #475569 !important;
    color: #c4b5fd !important;
    border-radius: 10px !important;
    font-weight: 600;
    transition: all 0.3s ease;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #7b68ee, #a78bfa) !important;
    color: white !important;
    border-color: transparent !important;
    transform: translateY(-2px);
}

/* ==================== ANIMATIONS ==================== */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.custom-card, .stat-mini, .alert-card {
    animation: fadeIn 0.4s ease-out;
}

/* ==================== FORM DARK ==================== */
div[data-testid="stForm"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 24px;
}
</style>
""", unsafe_allow_html=True)


# ================================================================
# UTILS
# ================================================================
def mga(x):
    return f"{int(x or 0):,}".replace(",", " ") + " Ar"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    c = get_conn()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS produits(
            id INTEGER PRIMARY KEY, code TEXT UNIQUE, nom TEXT, categorie TEXT,
            hauteur INTEGER, longueur INTEGER, largeur INTEGER, couleur TEXT,
            forme_pieds TEXT, prix_achat INTEGER, prix_vente INTEGER,
            stock INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS clients(
            id INTEGER PRIMARY KEY, nom TEXT, tel TEXT
        );
        CREATE TABLE IF NOT EXISTS fournisseurs(
            id INTEGER PRIMARY KEY, nom TEXT, tel TEXT
        );
        CREATE TABLE IF NOT EXISTS mouvements(
            id INTEGER PRIMARY KEY, date TEXT, produit_id INTEGER, type TEXT,
            qte INTEGER, pu INTEGER, tiers TEXT, ref TEXT
        );
        CREATE TABLE IF NOT EXISTS journal(
            id INTEGER PRIMARY KEY, date TEXT, type TEXT,
            description TEXT, montant INTEGER
        );
    """)
    try:
        c.execute("ALTER TABLE produits ADD COLUMN forme_pieds TEXT")
    except:
        pass
    c.commit()

init_db()
conn = get_conn()

# ================================================================
# LISTES DE CHOIX
# ================================================================
LISTE_PIEDS = [
    "/U", "/V", "/X", "/K", "/PLIABLE",
    "/TABOURET CARRE", "/TABOURET CERCLE"
]
LISTE_COULEURS = [
    "/BLANC UNIS", "/NOIR UNIS", "/GRIS MARBRE",
    "#1023", "#1025", "#805", "#806", "#506",
    "#16854", "#16855", "#1010", "#8042", "#8052",
    "#932", "#809", "#308 BM", "#7058", "#76-1"
]

MENU_ITEMS = [
    "📊 Tableau de bord",
    "📦 Produits",
    "📥 Entrées Stock",
    "📤 Ventes",
    "📒 Journalier",
    "💰 Comptabilité"
]


# ================================================================
# HELPERS
# ================================================================
def page_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div class="page-header">
        <div>
            <span class="icon">{icon}</span>
            <span class="title">{title}</span>
            <div class="subtitle">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    if os.path.exists("logo mm.jpg"):
        st.image("logo mm.jpg", use_container_width=True)
    else:
        st.markdown("""
        <div class="sidebar-logo">
            <h2>🏗️ M & M</h2>
            <p>Melamine & Metallique</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    page = st.radio(
        "Navigation",
        MENU_ITEMS,
        label_visibility="collapsed"
    )

    st.divider()

    # Mini stats
    prod_count = pd.read_sql("SELECT COUNT(*) as n FROM produits", conn).n[0]
    low_stock = pd.read_sql(
        "SELECT COUNT(*) as n FROM produits WHERE stock <= 3", conn
    ).n[0]
    total_stock = pd.read_sql(
        "SELECT COALESCE(SUM(stock),0) as n FROM produits", conn
    ).n[0]

    st.markdown(f"""
    <div class="sidebar-stats">
        <div class="stats-title">📈 Résumé rapide</div>
        <div class="stats-row">
            <div class="stat-item">
                <div class="stat-number" style="color: #a78bfa;">{prod_count}</div>
                <div class="stat-label">Produits</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" style="color: #6ee7b7;">{total_stock}</div>
                <div class="stat-label">En stock</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" style="color: #fca5a5;">{low_stock}</div>
                <div class="stat-label">Alertes</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("✨ By Lemur Tsena — v2.0 Dark")


# ================================================================
# 📊 TABLEAU DE BORD
# ================================================================
if page == "📊 Tableau de bord":
    page_header("📊", "Tableau de bord",
                "Vue d'ensemble de votre activité")

    prod = pd.read_sql("SELECT * FROM produits", conn)
    valeur_stock = (prod["stock"] * prod["prix_vente"]).sum() if not prod.empty else 0

    mois_actuel = datetime.now().strftime("%Y-%m") + "%"

    v_prod = pd.read_sql(
        "SELECT COALESCE(SUM(qte*pu),0) as val FROM mouvements "
        "WHERE type='VENTE' AND date LIKE ?",
        conn, params=(mois_actuel,)
    ).val[0]
    r_jour = pd.read_sql(
        "SELECT COALESCE(SUM(montant),0) as val FROM journal "
        "WHERE type='RECETTE' AND date LIKE ?",
        conn, params=(mois_actuel,)
    ).val[0]
    total_recettes = v_prod + r_jour

    a_prod = pd.read_sql(
        "SELECT COALESCE(SUM(qte*pu),0) as val FROM mouvements "
        "WHERE type='ACHAT' AND date LIKE ?",
        conn, params=(mois_actuel,)
    ).val[0]
    d_jour = pd.read_sql(
        "SELECT COALESCE(SUM(montant),0) as val FROM journal "
        "WHERE type='DEPENSE' AND date LIKE ?",
        conn, params=(mois_actuel,)
    ).val[0]
    total_depenses = a_prod + d_jour
    benefice = total_recettes - total_depenses

    # KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("💎 Valeur du stock", mga(valeur_stock))
    c2.metric("📈 Recettes du mois", mga(total_recettes))
    c3.metric("🏆 Bénéfice net", mga(benefice))

    st.markdown("<br>", unsafe_allow_html=True)

    # Stock + Alertes
    col_left, col_right = st.columns([3, 1])

    with col_left:
        st.markdown("### 📦 État des stocks")

        if not prod.empty:
            # Filtres
            fc1, fc2 = st.columns([1, 2])
            with fc1:
                cats = ["Toutes"] + sorted(prod["categorie"].dropna().unique().tolist())
                filtre_cat = st.selectbox("Catégorie", cats, key="db_fcat",
                                          label_visibility="collapsed")
            with fc2:
                search = st.text_input("🔍", placeholder="Rechercher un produit...",
                                       key="db_search", label_visibility="collapsed")

            prod_f = prod.copy()
            if filtre_cat != "Toutes":
                prod_f = prod_f[prod_f["categorie"] == filtre_cat]
            if search:
                mask = (
                    prod_f["nom"].str.contains(search, case=False, na=False) |
                    prod_f["code"].str.contains(search, case=False, na=False)
                )
                prod_f = prod_f[mask]

            display_cols = ["code", "nom", "categorie", "stock",
                            "longueur", "largeur", "hauteur", "forme_pieds"]
            st.dataframe(
                prod_f[display_cols].style.applymap(
                    lambda v: (
                        'background-color: rgba(239,68,68,0.15); color: #fca5a5'
                        if isinstance(v, (int, float)) and v <= 0
                        else (
                            'background-color: rgba(234,179,8,0.15); color: #fde047'
                            if isinstance(v, (int, float)) and v <= 3
                            else ''
                        )
                    ),
                    subset=['stock']
                ),
                use_container_width=True,
                height=420
            )
        else:
            st.info("🛒 Aucun produit enregistré.")

    with col_right:
        st.markdown("### ⚠️ Alertes")
        low_items = prod[prod["stock"] <= 3].sort_values("stock") if not prod.empty else pd.DataFrame()

        if not low_items.empty:
            for _, row in low_items.iterrows():
                if row["stock"] <= 0:
                    cls = "danger"
                    emoji = "🔴"
                else:
                    cls = "warning"
                    emoji = "🟡"
                st.markdown(f"""
                <div class="alert-card {cls}">
                    {emoji} <strong>{row['nom']}</strong><br>
                    <span style="color: #94a3b8; font-size: 0.8rem;">
                        Stock: {int(row['stock'])}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-card success">
                ✅ <strong>Tous les stocks sont OK</strong>
            </div>
            """, unsafe_allow_html=True)


# ================================================================
# 📦 PRODUITS
# ================================================================
elif page == "📦 Produits":
    page_header("📦", "Catalogue des Produits",
                "Gérez votre inventaire de meubles")

    df = pd.read_sql("SELECT * FROM produits", conn)

    tab_list, tab_add, tab_edit = st.tabs([
        "📋 Liste des produits",
        "➕ Nouveau produit",
        "✏️ Modifier / Supprimer"
    ])

    # ---- LISTE ----
    with tab_list:
        if not df.empty:
            fc1, fc2, fc3 = st.columns([1, 1, 2])
            with fc1:
                f_cat = st.selectbox(
                    "Catégorie",
                    ["Toutes"] + sorted(df["categorie"].dropna().unique().tolist()),
                    key="prod_fcat"
                )
            with fc2:
                f_coul = st.selectbox(
                    "Couleur",
                    ["Toutes"] + sorted(df["couleur"].dropna().unique().tolist()),
                    key="prod_fcoul"
                )
            with fc3:
                f_search = st.text_input("🔍 Recherche",
                                         placeholder="Nom, code...",
                                         key="prod_fsearch")

            df_view = df.copy()
            if f_cat != "Toutes":
                df_view = df_view[df_view["categorie"] == f_cat]
            if f_coul != "Toutes":
                df_view = df_view[df_view["couleur"] == f_coul]
            if f_search:
                mask = (
                    df_view["nom"].str.contains(f_search, case=False, na=False) |
                    df_view["code"].str.contains(f_search, case=False, na=False)
                )
                df_view = df_view[mask]

            # Mini stats
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.markdown(f"""
            <div class="stat-mini">
                <div class="number">{len(df_view)}</div>
                <div class="label">Produits</div>
            </div>""", unsafe_allow_html=True)
            sc2.markdown(f"""
            <div class="stat-mini">
                <div class="number" style="color:#6ee7b7;">{int(df_view['stock'].sum())}</div>
                <div class="label">Total stock</div>
            </div>""", unsafe_allow_html=True)
            sc3.markdown(f"""
            <div class="stat-mini">
                <div class="number" style="color:#86efac;">
                    {len(df_view[df_view['stock']>3])}
                </div>
                <div class="label">En stock</div>
            </div>""", unsafe_allow_html=True)
            sc4.markdown(f"""
            <div class="stat-mini">
                <div class="number" style="color:#fca5a5;">
                    {len(df_view[df_view['stock']<=0])}
                </div>
                <div class="label">Rupture</div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            df_display = df_view.drop(columns=["prix_achat", "id"])
            df_display["prix_vente"] = df_display["prix_vente"].apply(mga)
            st.dataframe(df_display, use_container_width=True, height=450)
        else:
            st.info("🛒 Aucun produit. Utilisez l'onglet ➕ pour en ajouter.")

    # ---- AJOUT ----
    with tab_add:
        st.markdown("""
        <div class="custom-card">
            💡 <strong>Info :</strong> Le <em>nom</em> et le <em>code</em>
            sont générés automatiquement à partir des caractéristiques.
        </div>
        """, unsafe_allow_html=True)

        with st.form("add_prod", clear_on_submit=True):
            st.markdown("#### 🏷️ Caractéristiques")
            c1, c2, c3 = st.columns(3)
            cat = c1.selectbox("Catégorie",
                               ["TABLE", "CHAISE", "BUREAU", "ETAGERE", "AUTRE"])
            coul = c2.selectbox("Couleur", LISTE_COULEURS)
            pieds = c3.selectbox("Forme des pieds", LISTE_PIEDS)

            st.markdown("#### 📐 Dimensions")
            c1, c2, c3 = st.columns(3)
            long = c1.number_input("Longueur (cm)", 0, step=5)
            larg = c2.number_input("Largeur (cm)", 0, step=5)
            haut = c3.number_input("Hauteur (cm)", 0, step=5)

            st.markdown("#### 💲 Tarification & Stock")
            c1, c2, c3 = st.columns(3)
            pa = c1.number_input("Prix d'achat (Ar)", 0, step=1000)
            pv = c2.number_input("Prix de vente (Ar)", 0, step=1000)
            stock = c3.number_input("Stock initial", 0)

            st.markdown("---")
            submitted = st.form_submit_button(
                "✅ Enregistrer le produit", use_container_width=True
            )
            if submitted:
                nom_auto = f"{cat}.{long}.{larg}.{pieds}"
                c_clean = coul.replace("/", "").replace("#", "")
                p_clean = pieds.replace("/", "")
                code_auto = (
                    f"{cat}-{long}-{larg}-{haut}-{c_clean}-{p_clean}"
                    .upper().replace(" ", "")
                )
                try:
                    conn.execute(
                        """INSERT INTO produits
                        (code,nom,categorie,hauteur,longueur,largeur,
                         couleur,forme_pieds,prix_achat,prix_vente,stock)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                        (code_auto, nom_auto, cat, haut, long, larg,
                         coul, pieds, pa, pv, stock)
                    )
                    conn.commit()
                    st.success(f"✅ Produit créé : **{nom_auto}** — Code : `{code_auto}`")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Ce code existe déjà ou données invalides.\n\n`{e}`")

    # ---- MODIFIER / SUPPRIMER ----
    with tab_edit:
        if not df.empty:
            p_edit = st.selectbox(
                "Sélectionnez un produit",
                df.itertuples(),
                format_func=lambda x: f"🪑 {x.nom}  —  [{x.code}]  (Stock: {x.stock})"
            )

            st.markdown(f"""
            <div class="custom-card">
                <div style="display:flex; gap:24px; flex-wrap:wrap;">
                    <div>📋 <strong>Nom :</strong> {p_edit.nom}</div>
                    <div>🏷️ <strong>Code :</strong> <code style="color:#a78bfa;">{p_edit.code}</code></div>
                    <div>🎨 <strong>Couleur :</strong> {p_edit.couleur}</div>
                    <div>📦 <strong>Stock :</strong> {p_edit.stock}</div>
                    <div>💰 <strong>Prix vente :</strong> {mga(p_edit.prix_vente)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("edit_prod"):
                c1, c2 = st.columns(2)
                n_pv = c1.number_input("💲 Nouveau prix vente (Ar)",
                                       value=int(p_edit.prix_vente), step=1000)
                n_stock = c2.number_input("📦 Nouveau stock",
                                          value=int(p_edit.stock))

                st.markdown("---")
                b1, b2 = st.columns(2)
                update = b1.form_submit_button("💾 Mettre à jour",
                                               use_container_width=True)
                delete = b2.form_submit_button("🗑️ Supprimer",
                                               use_container_width=True)

                if update:
                    conn.execute(
                        "UPDATE produits SET prix_vente=?, stock=? WHERE id=?",
                        (n_pv, n_stock, p_edit.id)
                    )
                    conn.commit()
                    st.success("✅ Produit mis à jour !")
                    st.rerun()
                if delete:
                    conn.execute("DELETE FROM produits WHERE id=?", (p_edit.id,))
                    conn.commit()
                    st.warning("🗑️ Produit supprimé.")
                    st.rerun()
        else:
            st.info("Aucun produit à modifier.")


# ================================================================
# 📥 ENTRÉES STOCK
# ================================================================
elif page == "📥 Entrées Stock":
    page_header("📥", "Entrée de Marchandise",
                "Enregistrez vos achats et approvisionnements")

    prod = pd.read_sql("SELECT id, code, nom, stock FROM produits", conn)
    four = pd.read_sql("SELECT * FROM fournisseurs", conn)

    col_form, col_hist = st.columns([1, 1])

    with col_form:
        st.markdown("### 📝 Nouvelle entrée")
        with st.form("entree", clear_on_submit=True):
            if not prod.empty:
                p = st.selectbox(
                    "📦 Produit", prod.itertuples(),
                    format_func=lambda x: f"{x.nom}  [{x.code}]  (Stock: {x.stock})"
                )
            else:
                st.warning("Aucun produit disponible.")
                p = None

            if not four.empty:
                f = st.selectbox("🏭 Fournisseur", four.itertuples(),
                                 format_func=lambda x: x.nom)
                f_nom = f.nom
            else:
                f_nom = st.text_input("🏭 Nom du fournisseur")

            c1, c2 = st.columns(2)
            qte = c1.number_input("📊 Quantité", 1, step=1)
            pu = c2.number_input("💲 Prix unitaire achat (Ar)", 0, step=1000)

            total = qte * pu
            st.markdown(f"""
            <div style="background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.2);
                 border-radius: 12px; padding: 14px; text-align: center; margin: 10px 0;">
                <span style="color: #6ee7b7; font-weight: 700; font-size: 1.1rem;">
                    Total : {mga(total)}
                </span>
            </div>
            """, unsafe_allow_html=True)

            submitted = st.form_submit_button("✅ Valider l'achat",
                                              use_container_width=True)
            if submitted and p is not None:
                conn.execute(
                    "INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers) "
                    "VALUES (?,?,?,?,?,?)",
                    (datetime.now().isoformat(), p.id, 'ACHAT', qte, pu, f_nom)
                )
                conn.execute(
                    "UPDATE produits SET stock=stock+?, prix_achat=? WHERE id=?",
                    (qte, pu, p.id)
                )
                conn.commit()
                st.success(f"✅ +{qte} unité(s) ajoutée(s) à **{p.nom}**")
                st.rerun()

    with col_hist:
        st.markdown("### 📜 Derniers achats")
        achats = pd.read_sql(
            """SELECT m.date, p.nom as produit, m.qte, m.pu,
                      (m.qte*m.pu) as total, m.tiers as fournisseur
               FROM mouvements m JOIN produits p ON m.produit_id=p.id
               WHERE m.type='ACHAT' ORDER BY m.date DESC LIMIT 15""",
            conn
        )
        if not achats.empty:
            achats["total"] = achats["total"].apply(mga)
            achats["pu"] = achats["pu"].apply(mga)
            achats["date"] = pd.to_datetime(achats["date"]).dt.strftime("%d/%m/%Y %H:%M")
            st.dataframe(achats, use_container_width=True, height=420)
        else:
            st.info("📭 Aucun achat enregistré.")


# ================================================================
# 📤 VENTES
# ================================================================
elif page == "📤 Ventes":
    page_header("📤", "Vente / Facturation",
                "Enregistrez vos ventes et générez des références")

    prod = pd.read_sql("SELECT * FROM produits WHERE stock>0", conn)
    cli = pd.read_sql("SELECT * FROM clients", conn)

    if not prod.empty:
        col_form, col_hist = st.columns([1, 1])

        with col_form:
            st.markdown("### 🛒 Nouvelle vente")
            with st.form("vente", clear_on_submit=True):
                p = st.selectbox(
                    "📦 Produit", prod.itertuples(),
                    format_func=lambda x: f"{x.nom}  (Stock: {x.stock})  —  {mga(x.prix_vente)}"
                )
                if not cli.empty:
                    c = st.selectbox("👤 Client", cli.itertuples(),
                                     format_func=lambda x: x.nom)
                    c_nom = c.nom
                else:
                    c_nom = st.text_input("👤 Nom du client")

                c1, c2 = st.columns(2)
                qte = c1.number_input("📊 Quantité", 1, max_value=int(p.stock))
                pu = c2.number_input("💲 Prix vente (Ar)", int(p.prix_vente), step=1000)

                total_vente = qte * pu
                marge = (pu - (p.prix_achat or 0)) * qte

                vc1, vc2 = st.columns(2)
                vc1.markdown(f"""
                <div style="background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.2);
                     border-radius: 12px; padding: 14px; text-align: center;">
                    <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;">Total</div>
                    <div style="color: #a5b4fc; font-weight: 700; font-size: 1.15rem;">
                        {mga(total_vente)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                vc2.markdown(f"""
                <div style="background: {'rgba(34,197,94,0.1)' if marge >= 0 else 'rgba(239,68,68,0.1)'};
                     border: 1px solid {'rgba(34,197,94,0.2)' if marge >= 0 else 'rgba(239,68,68,0.2)'};
                     border-radius: 12px; padding: 14px; text-align: center;">
                    <div style="color: #94a3b8; font-size: 0.75rem; text-transform: uppercase;">Marge</div>
                    <div style="color: {'#6ee7b7' if marge >= 0 else '#fca5a5'};
                         font-weight: 700; font-size: 1.15rem;">
                        {mga(marge)}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("✅ Enregistrer la vente",
                                                  use_container_width=True)
                if submitted:
                    ref = f"V{datetime.now().strftime('%y%m%d%H%M')}"
                    conn.execute(
                        "INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers,ref) "
                        "VALUES (?,?,?,?,?,?,?)",
                        (datetime.now().isoformat(), p.id, 'VENTE', qte, pu, c_nom, ref)
                    )
                    conn.execute(
                        "UPDATE produits SET stock=stock-? WHERE id=?",
                        (qte, p.id)
                    )
                    conn.commit()
                    st.success(f"✅ Vente enregistrée — Réf: `{ref}`")
                    st.balloons()
                    st.rerun()

        with col_hist:
            st.markdown("### 📜 Dernières ventes")
            ventes = pd.read_sql(
                """SELECT m.date, m.ref, p.nom as produit, m.qte, m.pu,
                          (m.qte*m.pu) as total, m.tiers as client
                   FROM mouvements m JOIN produits p ON m.produit_id=p.id
                   WHERE m.type='VENTE' ORDER BY m.date DESC LIMIT 15""",
                conn
            )
            if not ventes.empty:
                ventes["total"] = ventes["total"].apply(mga)
                ventes["pu"] = ventes["pu"].apply(mga)
                ventes["date"] = pd.to_datetime(ventes["date"]).dt.strftime("%d/%m/%Y %H:%M")
                st.dataframe(ventes, use_container_width=True, height=420)
            else:
                st.info("📭 Aucune vente enregistrée.")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 80px 20px;">
            <div style="font-size: 5rem; margin-bottom: 16px;">📦</div>
            <h3 style="color: #94a3b8 !important;">Aucun stock disponible</h3>
            <p style="color: #64748b;">
                Allez dans <strong>📥 Entrées Stock</strong> pour réapprovisionner.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ================================================================
# 📒 JOURNALIER
# ================================================================
elif page == "📒 Journalier":
    page_header("📒", "Journal des Opérations",
                "Suivez vos dépenses et recettes quotidiennes")

    df_j = pd.read_sql(
        "SELECT id, date, type, description, montant "
        "FROM journal ORDER BY date DESC", conn
    )

    # KPI du jour
    today = datetime.now().strftime("%Y-%m-%d")
    rec_today = pd.read_sql(
        "SELECT COALESCE(SUM(montant),0) as val FROM journal "
        "WHERE type='RECETTE' AND date LIKE ?",
        conn, params=(today + "%",)
    ).val[0]
    dep_today = pd.read_sql(
        "SELECT COALESCE(SUM(montant),0) as val FROM journal "
        "WHERE type='DEPENSE' AND date LIKE ?",
        conn, params=(today + "%",)
    ).val[0]

    kc1, kc2, kc3 = st.columns(3)
    kc1.metric("🟢 Recettes aujourd'hui", mga(rec_today))
    kc2.metric("🔴 Dépenses aujourd'hui", mga(dep_today))
    kc3.metric("📊 Solde du jour", mga(rec_today - dep_today))

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 3])

    with col1:
        t_add, t_edit = st.tabs(["➕ Ajouter", "✏️ Modifier / Suppr"])

        with t_add:
            with st.form("add_j", clear_on_submit=True):
                typ = st.selectbox(
                    "Type d'opération",
                    ["DEPENSE", "RECETTE"],
                    format_func=lambda x: f"{'🔴 Dépense' if x == 'DEPENSE' else '🟢 Recette'}"
                )
                des = st.text_input("📝 Description")
                mnt = st.number_input("💲 Montant (Ar)", 0, step=1000)
                dat = st.date_input("📅 Date", datetime.now())

                if mnt > 0:
                    color = "rgba(34,197,94,0.1)" if typ == "RECETTE" else "rgba(239,68,68,0.1)"
                    border = "rgba(34,197,94,0.2)" if typ == "RECETTE" else "rgba(239,68,68,0.2)"
                    txt_color = "#6ee7b7" if typ == "RECETTE" else "#fca5a5"
                    icon = "🟢" if typ == "RECETTE" else "🔴"
                    st.markdown(f"""
                    <div style="background: {color}; border: 1px solid {border};
                         border-radius: 12px; padding: 12px; text-align: center; margin: 8px 0;">
                        <span style="color: {txt_color}; font-weight: 700;">
                            {icon} {mga(mnt)}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                submitted = st.form_submit_button("✅ Enregistrer",
                                                  use_container_width=True)
                if submitted:
                    if des.strip() == "":
                        st.error("❌ Veuillez saisir une description.")
                    else:
                        conn.execute(
                            "INSERT INTO journal(date,type,description,montant) "
                            "VALUES (?,?,?,?)",
                            (dat.isoformat(), typ, des, mnt)
                        )
                        conn.commit()
                        st.success("✅ Opération enregistrée !")
                        st.rerun()

        with t_edit:
            if not df_j.empty:
                item = st.selectbox(
                    "Opération à modifier",
                    df_j.itertuples(),
                    format_func=lambda x: (
                        f"{'🔴' if x.type == 'DEPENSE' else '🟢'} "
                        f"{x.date[:10]} | {x.description} | {mga(x.montant)}"
                    )
                )
                with st.form("edit_j"):
                    e_des = st.text_input("📝 Description", value=item.description)
                    e_mnt = st.number_input("💲 Montant", value=int(item.montant), step=1000)

                    st.markdown("---")
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 Mettre à jour",
                                             use_container_width=True):
                        conn.execute(
                            "UPDATE journal SET description=?, montant=? WHERE id=?",
                            (e_des, e_mnt, item.id)
                        )
                        conn.commit()
                        st.success("✅ Mis à jour !")
                        st.rerun()
                    if b2.form_submit_button("🗑️ Supprimer",
                                             use_container_width=True):
                        conn.execute("DELETE FROM journal WHERE id=?", (item.id,))
                        conn.commit()
                        st.warning("🗑️ Supprimé.")
                        st.rerun()
            else:
                st.info("Aucune opération enregistrée.")

    with col2:
        if not df_j.empty:
            df_display = df_j.drop(columns=["id"]).copy()
            df_display["montant"] = df_display["montant"].apply(mga)
            df_display["type"] = df_display["type"].apply(
                lambda x: "🟢 RECETTE" if x == "RECETTE" else "🔴 DÉPENSE"
            )
            st.dataframe(df_display, use_container_width=True, height=480)

            # Export
            csv = df_j.drop(columns=["id"]).to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Exporter en CSV", csv, "journal.csv",
                "text/csv", use_container_width=True
            )
        else:
            st.info("📭 Aucune donnée.")


# ================================================================
# 💰 COMPTABILITÉ
# ================================================================
else:
    page_header("💰", "Comptabilité Générale",
                "Synthèse financière complète")

    mouv = pd.read_sql("SELECT type, (qte*pu) as montant FROM mouvements", conn)
    jour = pd.read_sql("SELECT type, montant FROM journal", conn)

    recettes = (
        mouv[mouv.type == 'VENTE']["montant"].sum() +
        jour[jour.type == 'RECETTE']["montant"].sum()
    )
    depenses = (
        mouv[mouv.type == 'ACHAT']["montant"].sum() +
        jour[jour.type == 'DEPENSE']["montant"].sum()
    )
    profit = recettes - depenses

    # KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("💚 Total Recettes", mga(recettes))
    c2.metric("❤️ Total Dépenses", mga(depenses))
    c3.metric("🏆 Profit Global", mga(profit))

    st.markdown("<br>", unsafe_allow_html=True)

    col_chart, col_detail = st.columns([2, 1])

    with col_chart:
        st.markdown("### 📈 Évolution financière")

        m_plot = pd.read_sql(
            "SELECT substr(date,1,10) as date, (qte*pu) as montant, type "
            "FROM mouvements", conn
        )
        j_plot = pd.read_sql(
            "SELECT substr(date,1,10) as date, montant, type FROM journal", conn
        )
        total_data = pd.concat([m_plot, j_plot])

        if not total_data.empty:
            total_data['Recettes'] = total_data.apply(
                lambda x: x['montant'] if x['type'] in ['VENTE', 'RECETTE'] else 0,
                axis=1
            )
            total_data['Dépenses'] = total_data.apply(
                lambda x: x['montant'] if x['type'] in ['ACHAT', 'DEPENSE'] else 0,
                axis=1
            )
            chart_data = total_data.groupby('date')[['Recettes', 'Dépenses']].sum()
            st.line_chart(chart_data)

            st.markdown("### 📊 Solde cumulé")
            chart_data['Solde'] = (chart_data['Recettes'] - chart_data['Dépenses']).cumsum()
            st.area_chart(chart_data[['Solde']])
        else:
            st.info("📊 Pas encore de données pour les graphiques.")

    with col_detail:
        st.markdown("### 📋 Répartition")

        # Ventes par catégorie
        ventes_detail = pd.read_sql(
            """SELECT p.categorie, SUM(m.qte*m.pu) as total
               FROM mouvements m JOIN produits p ON m.produit_id=p.id
               WHERE m.type='VENTE' GROUP BY p.categorie
               ORDER BY total DESC""",
            conn
        )
        if not ventes_detail.empty:
            st.markdown("**🏷️ Ventes par catégorie**")
            total_ventes = ventes_detail['total'].sum()
            for _, row in ventes_detail.iterrows():
                pct = (row['total'] / total_ventes) * 100 if total_ventes > 0 else 0
                st.markdown(f"""
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between;
                         font-size: 0.85rem; margin-bottom: 6px;">
                        <span style="color: #cbd5e1;">{row['categorie']}</span>
                        <span style="font-weight: 600; color: #a78bfa;">
                            {mga(row['total'])}
                        </span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: {pct}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Indicateur Profit / Perte
        if profit >= 0:
            bg = "rgba(34,197,94,0.1)"
            border = "rgba(34,197,94,0.2)"
            emoji = "🎉"
            msg = "Vous êtes en bénéfice !"
            color = "#6ee7b7"
        else:
            bg = "rgba(239,68,68,0.1)"
            border = "rgba(239,68,68,0.2)"
            emoji = "⚠️"
            msg = "Attention, vous êtes en perte."
            color = "#fca5a5"

        st.markdown(f"""
        <div style="background: {bg}; border: 1px solid {border};
             border-radius: 16px; padding: 28px; text-align: center;">
            <div style="font-size: 3.5rem;">{emoji}</div>
            <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 10px;">
                {msg}
            </div>
            <div style="font-size: 1.8rem; font-weight: 800;
                 color: {color}; margin-top: 10px;">
                {mga(profit)}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Export
        all_mouv = pd.read_sql("SELECT * FROM mouvements", conn)
        all_jour = pd.read_sql("SELECT * FROM journal", conn)
        if not all_mouv.empty or not all_jour.empty:
            st.markdown("**📥 Exporter les données**")
            ec1, ec2 = st.columns(2)
            if not all_mouv.empty:
                csv_m = all_mouv.to_csv(index=False).encode("utf-8")
                ec1.download_button(
                    "📦 Mouvements", csv_m, "mouvements.csv",
                    "text/csv", use_container_width=True
                )
            if not all_jour.empty:
                csv_j = all_jour.to_csv(index=False).encode("utf-8")
                ec2.download_button(
                    "📒 Journal", csv_j, "journal.csv",
                    "text/csv", use_container_width=True
                )
