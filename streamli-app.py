```python
import streamlit as st
import sqlite3, pandas as pd
from datetime import datetime
import os

DB = "gestion_tables_mga.db"

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Melamine & Metallique",
    layout="wide",
    page_icon="🏗️",
    initial_sidebar_state="expanded"
)

# --- CSS MODE SOMBRE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ===== BASE SOMBRE ===== */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
}

/* ===== FOND PRINCIPAL ===== */
.stApp {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%) !important;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #010409 0%, #0d1117 40%, #161b22 100%) !important;
    border-right: 1px solid #30363d !important;
}
section[data-testid="stSidebar"] * {
    color: #c9d1d9 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #8b949e !important;
    font-size: 0.95rem;
    padding: 6px 10px;
    border-radius: 8px;
    transition: all 0.2s;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: #58a6ff !important;
    background: rgba(88, 166, 255, 0.08) !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #21262d !important;
}

/* ===== CARTES MÉTRIQUES ===== */
div[data-testid="stMetric"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 16px !important;
    padding: 20px 24px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4) !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease !important;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 8px 32px rgba(88,166,255,0.15) !important;
    border-color: #58a6ff !important;
}
div[data-testid="stMetric"] label {
    color: #8b949e !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #e6edf3 !important;
    font-weight: 700 !important;
    font-size: 1.5rem !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stMetric"] {
    border-top: 3px solid #58a6ff !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetric"] {
    border-top: 3px solid #3fb950 !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetric"] {
    border-top: 3px solid #f78166 !important;
}

/* ===== TITRES ===== */
h1, h2, h3 {
    color: #e6edf3 !important;
    font-weight: 700 !important;
}

/* ===== DATAFRAMES ===== */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #30363d !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
}
.stDataFrame iframe {
    background: #161b22 !important;
}

/* ===== BOUTONS ===== */
.stButton > button {
    background: #21262d !important;
    color: #c9d1d9 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background: #30363d !important;
    border-color: #58a6ff !important;
    color: #58a6ff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(88,166,255,0.15) !important;
}

/* ===== FORM SUBMIT ===== */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(31, 111, 235, 0.3) !important;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(31, 111, 235, 0.45) !important;
    background: linear-gradient(135deg, #388bfd 0%, #58a6ff 100%) !important;
}

/* ===== INPUTS ===== */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
    background: #0d1117 !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    transition: border-color 0.3s ease !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.15) !important;
}
.stSelectbox > div > div {
    background: #0d1117 !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
}
.stSelectbox > div > div:focus-within {
    border-color: #58a6ff !important;
}
[data-baseweb="select"] {
    background: #0d1117 !important;
}
[data-baseweb="popover"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
}
[data-baseweb="option"] {
    background: #161b22 !important;
    color: #e6edf3 !important;
}
[data-baseweb="option"]:hover {
    background: #21262d !important;
}

/* ===== DATE INPUT ===== */
.stDateInput > div > div > input {
    background: #0d1117 !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
}

/* ===== EXPANDERS ===== */
.streamlit-expanderHeader {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    color: #c9d1d9 !important;
    font-weight: 600 !important;
}
.streamlit-expanderHeader:hover {
    border-color: #58a6ff !important;
    color: #58a6ff !important;
}
.streamlit-expanderContent {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-top: none !important;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px !important;
    background: #161b22 !important;
    border-radius: 12px !important;
    padding: 6px !important;
    border: 1px solid #30363d !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 18px !important;
    font-weight: 500 !important;
    color: #8b949e !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #e6edf3 !important;
    background: #21262d !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1f6feb, #388bfd) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(31,111,235,0.3) !important;
}

/* ===== ALERTES ===== */
.stAlert {
    border-radius: 12px !important;
    border: 1px solid #30363d !important;
}
div[data-testid="stAlert"] {
    background: #161b22 !important;
    border-radius: 12px !important;
}

/* ===== FORMS ===== */
[data-testid="stForm"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 16px !important;
    padding: 20px !important;
}

/* ===== DIVIDERS ===== */
hr {
    border-color: #21262d !important;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #161b22;
}
::-webkit-scrollbar-thumb {
    background: #30363d;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: #58a6ff;
}

/* ===== CUSTOM CLASSES ===== */
.dark-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.dark-card:hover {
    border-color: #58a6ff;
    box-shadow: 0 8px 30px rgba(88,166,255,0.1);
    transition: all 0.3s ease;
}
.stat-mini {
    text-align: center;
    padding: 16px 12px;
    border-radius: 12px;
    background: #161b22;
    border: 1px solid #30363d;
}
.stat-mini .number {
    font-size: 1.8rem;
    font-weight: 700;
    color: #58a6ff;
}
.stat-mini .label {
    font-size: 0.75rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 4px;
}
.badge-ok {
    background: rgba(63,185,80,0.15);
    color: #3fb950;
    border: 1px solid rgba(63,185,80,0.3);
    padding: 3px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.82rem;
}
.badge-low {
    background: rgba(210,153,34,0.15);
    color: #d29922;
    border: 1px solid rgba(210,153,34,0.3);
    padding: 3px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.82rem;
}
.badge-out {
    background: rgba(248,81,73,0.15);
    color: #f85149;
    border: 1px solid rgba(248,81,73,0.3);
    padding: 3px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.82rem;
}
.page-header {
    padding: 16px 0 20px 0;
    border-bottom: 1px solid #21262d;
    margin-bottom: 28px;
}
.page-title {
    font-size: 1.9rem;
    font-weight: 700;
    color: #e6edf3;
    display: flex;
    align-items: center;
    gap: 12px;
}
.page-subtitle {
    color: #8b949e;
    font-size: 0.9rem;
    margin-top: 4px;
    margin-left: 2px;
}
.glow-blue { color: #58a6ff; }
.glow-green { color: #3fb950; }
.glow-red { color: #f85149; }
.glow-orange { color: #d29922; }

.progress-bar-bg {
    background: #21262d;
    border-radius: 10px;
    height: 8px;
    overflow: hidden;
    margin-top: 4px;
}
.progress-bar-fill {
    background: linear-gradient(90deg, #1f6feb, #58a6ff);
    height: 100%;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# --- UTILS ---
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
        CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY, nom TEXT, tel TEXT);
        CREATE TABLE IF NOT EXISTS fournisseurs(id INTEGER PRIMARY KEY, nom TEXT, tel TEXT);
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

# --- LISTES ---
LISTE_PIEDS = ["/U", "/V", "/X", "/K", "/PLIABLE", "/TABOURET CARRE", "/TABOURET CERCLE"]
LISTE_COULEURS = [
    "/BLANC UNIS", "/NOIR UNIS", "/GRIS MARBRE",
    "#1023", "#1025", "#805", "#806", "#506",
    "#16854", "#16855", "#1010", "#8042", "#8052",
    "#932", "#809", "#308 BM", "#7058", "#76-1"
]

PAGES = [
    "📊 Tableau de bord",
    "📦 Produits",
    "📥 Entrées Stock",
    "📤 Ventes",
    "📒 Journalier",
    "💰 Comptabilité"
]

def page_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">{icon} {title}</div>
        <div class="page-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def dark_card(content_html, border_color="#30363d"):
    st.markdown(f"""
    <div class="dark-card" style="border-color:{border_color};">
        {content_html}
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# --- SIDEBAR ---
# ============================================================
with st.sidebar:
    if os.path.exists("logo mm.jpg"):
        st.image("logo mm.jpg", use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding: 24px 10px 8px 10px;">
            <div style="font-size: 2.5rem;">🏗️</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #58a6ff; margin-top: 6px;">
                Melamine & Metallique
            </div>
            <div style="font-size: 0.75rem; color: #8b949e; margin-top: 4px;">
                Système de gestion
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    page = st.radio("Navigation", PAGES, label_visibility="collapsed")

    st.divider()

    # Mini stats
    try:
        prod_count = pd.read_sql("SELECT COUNT(*) as n FROM produits", conn).n[0]
        low_stock  = pd.read_sql("SELECT COUNT(*) as n FROM produits WHERE stock <= 3", conn).n[0]
        out_stock  = pd.read_sql("SELECT COUNT(*) as n FROM produits WHERE stock <= 0", conn).n[0]
    except:
        prod_count = low_stock = out_stock = 0

    st.markdown(f"""
    <div style="background:#0d1117; border:1px solid #21262d; border-radius:14px;
         padding:16px; margin-bottom:12px;">
        <div style="color:#8b949e; font-size:0.72rem; text-transform:uppercase;
             letter-spacing:1px; margin-bottom:12px;">
            📈 Résumé rapide
        </div>
        <div style="display:flex; justify-content:space-between; gap:8px;">
            <div style="text-align:center; flex:1; background:#161b22;
                 border-radius:10px; padding:10px 4px; border:1px solid #30363d;">
                <div style="color:#58a6ff; font-size:1.4rem; font-weight:700;">
                    {prod_count}
                </div>
                <div style="color:#8b949e; font-size:0.68rem; margin-top:2px;">
                    Produits
                </div>
            </div>
            <div style="text-align:center; flex:1; background:#161b22;
                 border-radius:10px; padding:10px 4px; border:1px solid #30363d;">
                <div style="color:#d29922; font-size:1.4rem; font-weight:700;">
                    {low_stock}
                </div>
                <div style="color:#8b949e; font-size:0.68rem; margin-top:2px;">
                    Stock bas
                </div>
            </div>
            <div style="text-align:center; flex:1; background:#161b22;
                 border-radius:10px; padding:10px 4px; border:1px solid #30363d;">
                <div style="color:#f85149; font-size:1.4rem; font-weight:700;">
                    {out_stock}
                </div>
                <div style="color:#8b949e; font-size:0.68rem; margin-top:2px;">
                    Rupture
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("✨ By Lemur Tsena — v2.0 Dark")


# ============================================================
# --- TABLEAU DE BORD ---
# ============================================================
if page == "📊 Tableau de bord":
    page_header("📊", "Tableau de bord", "Vue d'ensemble de votre activité")

    prod = pd.read_sql("SELECT * FROM produits", conn)
    valeur_stock = (prod["stock"] * prod["prix_vente"]).sum()

    mois_actuel = datetime.now().strftime("%Y-%m") + "%"
    v_prod  = pd.read_sql("SELECT SUM(qte*pu) as val FROM mouvements WHERE type='VENTE' AND date LIKE ?",  conn, params=(mois_actuel,)).val[0] or 0
    r_jour  = pd.read_sql("SELECT SUM(montant) as val FROM journal WHERE type='RECETTE' AND date LIKE ?",  conn, params=(mois_actuel,)).val[0] or 0
    a_prod  = pd.read_sql("SELECT SUM(qte*pu) as val FROM mouvements WHERE type='ACHAT' AND date LIKE ?",  conn, params=(mois_actuel,)).val[0] or 0
    d_jour  = pd.read_sql("SELECT SUM(montant) as val FROM journal WHERE type='DEPENSE' AND date LIKE ?",  conn, params=(mois_actuel,)).val[0] or 0

    total_recettes = v_prod + r_jour
    total_depenses = a_prod + d_jour
    benefice = total_recettes - total_depenses

    c1, c2, c3 = st.columns(3)
    c1.metric("💎 Valeur du stock",     mga(valeur_stock))
    c2.metric("📈 Recettes (Mois)",      mga(total_recettes))
    c3.metric("🏆 Bénéfice Net (Mois)", mga(benefice))

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 1])

    with col_left:
        st.markdown("### 📦 État des stocks")
        if not prod.empty:
            fc1, fc2 = st.columns([1, 3])
            cats    = ["Toutes"] + sorted(prod["categorie"].dropna().unique().tolist())
            f_cat   = fc1.selectbox("Catégorie", cats, key="db_fcat",
                                    label_visibility="collapsed")
            f_srch  = fc2.text_input("🔍 Recherche...", key="db_srch",
                                     placeholder="Nom ou code...")

            pf = prod.copy()
            if f_cat != "Toutes":
                pf = pf[pf["categorie"] == f_cat]
            if f_srch:
                mask = (
                    pf["nom"].str.contains(f_srch, case=False, na=False) |
                    pf["code"].str.contains(f_srch, case=False, na=False)
                )
                pf = pf[mask]

            cols_show = ["code","nom","categorie","stock","longueur","largeur","hauteur","forme_pieds"]
            st.dataframe(
                pf[cols_show].style.applymap(
                    lambda v: 'background-color: rgba(248,81,73,0.15); color:#f85149'
                    if isinstance(v,(int,float)) and v<=0
                    else ('background-color: rgba(210,153,34,0.15); color:#d29922'
                          if isinstance(v,(int,float)) and 0<v<=3 else ''),
                    subset=["stock"]
                ),
                use_container_width=True, height=400
            )
        else:
            st.info("Aucun produit. Ajoutez-en dans 📦 Produits.")

    with col_right:
        st.markdown("### ⚠️ Alertes")
        low_items = prod[prod["stock"] <= 3].sort_values("stock")
        if not low_items.empty:
            for _, row in low_items.iterrows():
                if row["stock"] <= 0:
                    ic, bg, tc = "🔴", "rgba(248,81,73,0.12)", "#f85149"
                else:
                    ic, bg, tc = "🟡", "rgba(210,153,34,0.12)", "#d29922"
                st.markdown(f"""
                <div style="background:{bg}; border:1px solid {tc}33;
                     border-radius:10px; padding:10px 14px; margin-bottom:8px;">
                    {ic} <strong style="color:{tc};">{row['nom']}</strong><br>
                    <span style="color:#8b949e; font-size:0.82rem;">
                        Stock : {int(row['stock'])}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(63,185,80,0.1); border:1px solid rgba(63,185,80,0.3);
                 border-radius:12px; padding:24px; text-align:center;">
                <div style="font-size:2rem;">✅</div>
                <div style="color:#3fb950; font-weight:600; margin-top:6px;">
                    Tous les stocks sont OK
                </div>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# --- PRODUITS ---
# ============================================================
elif page == "📦 Produits":
    page_header("📦", "Catalogue des Produits", "Gérez votre inventaire")

    df = pd.read_sql("SELECT * FROM produits", conn)

    tab_list, tab_add, tab_edit = st.tabs(
        ["📋 Liste", "➕ Nouveau produit", "✏️ Modifier / Supprimer"]
    )

    with tab_list:
        if not df.empty:
            fc1, fc2, fc3 = st.columns([1, 1, 2])
            f_cat  = fc1.selectbox("Catégorie",
                                   ["Toutes"] + sorted(df["categorie"].dropna().unique().tolist()),
                                   key="pl_cat")
            f_coul = fc2.selectbox("Couleur",
                                   ["Toutes"] + sorted(df["couleur"].dropna().unique().tolist()),
                                   key="pl_coul")
            f_srch = fc3.text_input("🔍 Recherche", placeholder="Nom, code...", key="pl_srch")

            dv = df.copy()
            if f_cat  != "Toutes": dv = dv[dv["categorie"] == f_cat]
            if f_coul != "Toutes": dv = dv[dv["couleur"]   == f_coul]
            if f_srch:
                dv = dv[dv["nom"].str.contains(f_srch, case=False, na=False) |
                        dv["code"].str.contains(f_srch, case=False, na=False)]

            # Stats rapides
            sc1, sc2, sc3, sc4 = st.columns(4)
            for col, num, label, color in [
                (sc1, len(dv),                         "Produits",  "#58a6ff"),
                (sc2, int(dv['stock'].sum()),           "Total stock","#e6edf3"),
                (sc3, len(dv[dv['stock']>3]),           "En stock",  "#3fb950"),
                (sc4, len(dv[dv['stock']<=0]),          "Rupture",   "#f85149"),
            ]:
                col.markdown(f"""
                <div class="stat-mini">
                    <div class="number" style="color:{color};">{num}</div>
                    <div class="label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            dd = dv.drop(columns=["prix_achat","id"])
            dd["prix_vente"] = dd["prix_vente"].apply(mga)
            st.dataframe(dd, use_container_width=True, height=420)
        else:
            st.info("Aucun produit. Utilisez l'onglet ➕.")

    with tab_add:
        st.markdown("""
        <div class="dark-card" style="border-color:#1f6feb44;">
            <span style="color:#58a6ff;">💡</span>
            Le <strong>nom</strong> et le <strong>code</strong>
            sont générés automatiquement depuis les caractéristiques.
        </div>
        """, unsafe_allow_html=True)

        with st.form("add_prod", clear_on_submit=True):
            st.markdown("#### 🏷️ Caractéristiques")
            c1, c2, c3 = st.columns(3)
            cat  = c1.selectbox("Catégorie", ["TABLE","CHAISE","BUREAU","ETAGERE","AUTRE"])
            coul = c2.selectbox("Couleur", LISTE_COULEURS)
            pieds= c3.selectbox("Forme des pieds", LISTE_PIEDS)

            st.markdown("#### 📐 Dimensions")
            c1, c2, c3 = st.columns(3)
            long = c1.number_input("Longueur (cm)", 0, step=5)
            larg = c2.number_input("Largeur (cm)",  0, step=5)
            haut = c3.number_input("Hauteur (cm)",  0, step=5)

            st.markdown("#### 💲 Prix & Stock")
            c1, c2, c3 = st.columns(3)
            pa    = c1.number_input("Prix d'achat (Ar)", 0, step=1000)
            pv    = c2.number_input("Prix de vente (Ar)", 0, step=1000)
            stock = c3.number_input("Stock initial", 0)

            st.markdown("---")
            if st.form_submit_button("✅ Enregistrer le produit", use_container_width=True):
                nom_auto  = f"{cat}.{long}.{larg}.{pieds}"
                c_clean   = coul.replace("/","").replace("#","")
                p_clean   = pieds.replace("/","")
                code_auto = f"{cat}-{long}-{larg}-{haut}-{c_clean}-{p_clean}".upper().replace(" ","")
                try:
                    conn.execute(
                        "INSERT INTO produits(code,nom,categorie,hauteur,longueur,largeur,"
                        "couleur,forme_pieds,prix_achat,prix_vente,stock) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        (code_auto,nom_auto,cat,haut,long,larg,coul,pieds,pa,pv,stock)
                    )
                    conn.commit()
                    st.success(f"✅ Produit créé : **{nom_auto}** — Code : `{code_auto}`")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Ce code existe déjà ou données invalides.\n\n`{e}`")

    with tab_edit:
        if not df.empty:
            p_edit = st.selectbox(
                "Sélectionnez un produit",
                df.itertuples(),
                format_func=lambda x: f"🪑 {x.nom}  —  [{x.code}]  (Stock: {x.stock})"
            )
            st.markdown(f"""
            <div class="dark-card">
                <div style="display:flex; flex-wrap:wrap; gap:20px; color:#c9d1d9;">
                    <div>📋 <strong>Nom :</strong> {p_edit.nom}</div>
                    <div>🏷️ <strong>Code :</strong>
                        <code style="background:#0d1117; padding:2px 8px; border-radius:6px;
                        color:#58a6ff;">{p_edit.code}</code>
                    </div>
                    <div>🎨 <strong>Couleur :</strong> {p_edit.couleur}</div>
                    <div>📦 <strong>Stock :</strong>
                        <span style="color:{'#f85149' if p_edit.stock<=0 else '#d29922' if p_edit.stock<=3 else '#3fb950'};">
                            {p_edit.stock}
                        </span>
                    </div>
                    <div>💰 <strong>Prix vente :</strong>
                        <span style="color:#58a6ff;">{mga(p_edit.prix_vente)}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("edit_prod"):
                c1, c2 = st.columns(2)
                n_pv    = c1.number_input("💲 Prix vente (Ar)", value=int(p_edit.prix_vente), step=1000)
                n_stock = c2.number_input("📦 Stock",            value=int(p_edit.stock))

                st.markdown("---")
                b1, b2 = st.columns(2)
                upd = b1.form_submit_button("💾 Mettre à jour",  use_container_width=True)
                dlt = b2.form_submit_button("🗑️ Supprimer",      use_container_width=True)

                if upd:
                    conn.execute("UPDATE produits SET prix_vente=?, stock=? WHERE id=?",
                                 (n_pv, n_stock, p_edit.id))
                    conn.commit(); st.success("✅ Mis à jour !"); st.rerun()
                if dlt:
                    conn.execute("DELETE FROM produits WHERE id=?", (p_edit.id,))
                    conn.commit(); st.warning("🗑️ Supprimé."); st.rerun()
        else:
            st.info("Aucun produit à modifier.")


# ============================================================
# --- ENTRÉES STOCK ---
# ============================================================
elif page == "📥 Entrées Stock":
    page_header("📥", "Entrée de Marchandise", "Approvisionnement & achats")

    prod = pd.read_sql("SELECT id, code, nom, stock FROM produits", conn)
    four = pd.read_sql("SELECT * FROM fournisseurs", conn)

    col_form, col_hist = st.columns([1, 1])

    with col_form:
        st.markdown("### 📝 Nouvelle entrée")
        with st.form("entree", clear_on_submit=True):
            p = st.selectbox("📦 Produit", prod.itertuples(),
                             format_func=lambda x: f"{x.nom}  [{x.code}]  (Stock: {x.stock})")
            f_nom = (
                st.selectbox("🏭 Fournisseur", four.itertuples(),
                             format_func=lambda x: x.nom).nom
                if not four.empty
                else st.text_input("🏭 Nom du fournisseur")
            )
            c1, c2 = st.columns(2)
            qte = c1.number_input("📊 Quantité", 1, step=1)
            pu  = c2.number_input("💲 Prix unitaire (Ar)", 0, step=1000)

            total = qte * pu
            st.markdown(f"""
            <div style="background:rgba(31,111,235,0.1); border:1px solid rgba(31,111,235,0.3);
                 border-radius:10px; padding:14px; text-align:center; margin:10px 0;">
                <span style="color:#58a6ff; font-weight:600; font-size:1.1rem;">
                    Total : {mga(total)}
                </span>
            </div>
            """, unsafe_allow_html=True)

            if st.form_submit_button("✅ Valider l'achat", use_container_width=True):
                conn.execute(
                    "INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers) VALUES(?,?,?,?,?,?)",
                    (datetime.now().isoformat(), p.id, 'ACHAT', qte, pu, f_nom)
                )
                conn.execute(
                    "UPDATE produits SET stock=stock+?, prix_achat=? WHERE id=?",
                    (qte, pu, p.id)
                )
                conn.commit()
                st.success(f"✅ +{qte} unité(s) ajoutée(s) pour **{p.nom}**")
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
            achats["pu"]    = achats["pu"].apply(mga)
            achats["date"]  = pd.to_datetime(achats["date"]).dt.strftime("%d/%m/%Y %H:%M")
            st.dataframe(achats, use_container_width=True, height=420)
        else:
            st.info("Aucun achat enregistré.")


# ============================================================
# --- VENTES ---
# ============================================================
elif page == "📤 Ventes":
    page_header("📤", "Vente / Facturation", "Enregistrez vos ventes")

    prod = pd.read_sql("SELECT * FROM produits WHERE stock>0", conn)
    cli  = pd.read_sql("SELECT * FROM clients", conn)

    if not prod.empty:
        col_form, col_hist = st.columns([1, 1])

        with col_form:
            st.markdown("### 🛒 Nouvelle vente")
            with st.form("vente", clear_on_submit=True):
                p = st.selectbox("📦 Produit", prod.itertuples(),
                                 format_func=lambda x: f"{x.nom}  (Stock:{x.stock}) — {mga(x.prix_vente)}")
                c_nom = (
                    st.selectbox("👤 Client", cli.itertuples(),
                                 format_func=lambda x: x.nom).nom
                    if not cli.empty
                    else st.text_input("👤 Nom du client")
                )
                c1, c2 = st.columns(2)
                qte = c1.number_input("📊 Quantité", 1, max_value=int(p.stock))
                pu  = c2.number_input("💲 Prix vente (Ar)", int(p.prix_vente), step=1000)

                total_v = qte * pu
                marge   = (pu - (p.prix_achat or 0)) * qte
                vc1, vc2 = st.columns(2)
                vc1.markdown(f"""
                <div style="background:rgba(31,111,235,0.1); border:1px solid rgba(31,111,235,0.3);
                     border-radius:10px; padding:12px; text-align:center;">
                    <div style="color:#8b949e; font-size:0.78rem;">TOTAL</div>
                    <div style="color:#58a6ff; font-weight:700; font-size:1.15rem;">
                        {mga(total_v)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                vc2.markdown(f"""
                <div style="background:{'rgba(63,185,80,0.1)' if marge>=0 else 'rgba(248,81,73,0.1)'};
                     border:1px solid {'rgba(63,185,80,0.3)' if marge>=0 else 'rgba(248,81,73,0.3)'};
                     border-radius:10px; padding:12px; text-align:center;">
                    <div style="color:#8b949e; font-size:0.78rem;">MARGE</div>
                    <div style="color:{'#3fb950' if marge>=0 else '#f85149'};
                         font-weight:700; font-size:1.15rem;">
                        {mga(marge)}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("✅ Enregistrer la vente", use_container_width=True):
                    ref = f"V{datetime.now().strftime('%y%m%d%H%M')}"
                    conn.execute(
                        "INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers,ref) "
                        "VALUES(?,?,?,?,?,?,?)",
                        (datetime.now().isoformat(), p.id, 'VENTE', qte, pu, c_nom, ref)
                    )
                    conn.execute("UPDATE produits SET stock=stock-? WHERE id=?", (qte, p.id))
                    conn.commit()
                    st.success(f"✅ Vente enregistrée — Réf : `{ref}`")
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
                ventes["pu"]    = ventes["pu"].apply(mga)
                ventes["date"]  = pd.to_datetime(ventes["date"]).dt.strftime("%d/%m/%Y %H:%M")
                st.dataframe(ventes, use_container_width=True, height=420)
            else:
                st.info("Aucune vente enregistrée.")
    else:
        st.markdown("""
        <div style="text-align:center; padding:70px 20px;">
            <div style="font-size:4rem;">📦</div>
            <h3 style="color:#8b949e;">Aucun stock disponible</h3>
            <p style="color:#6e7681;">
                Allez dans <strong style="color:#58a6ff;">📥 Entrées Stock</strong>
                pour réapprovisionner.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# --- JOURNALIER ---
# ============================================================
elif page == "📒 Journalier":
    page_header("📒", "Journal des Opérations", "Dépenses & recettes quotidiennes")

    df_j = pd.read_sql(
        "SELECT id, date, type, description, montant FROM journal ORDER BY date DESC", conn
    )

    col1, col2 = st.columns([2, 3])

    with col1:
        t_add, t_edit = st.tabs(["➕ Ajouter", "✏️ Modifier / Suppr"])

        with t_add:
            with st.form("add_j", clear_on_submit=True):
                typ = st.selectbox("Type", ["DEPENSE","RECETTE"],
                                   format_func=lambda x:
                                   "🔴 Dépense" if x=="DEPENSE" else "🟢 Recette")
                des = st.text_input("📝 Description")
                mnt = st.number_input("💲 Montant (Ar)", 0, step=1000)
                dat = st.date_input("📅 Date", datetime.now())

                if mnt > 0:
                    bg  = "rgba(63,185,80,0.1)"  if typ=="RECETTE" else "rgba(248,81,73,0.1)"
                    brd = "rgba(63,185,80,0.3)"  if typ=="RECETTE" else "rgba(248,81,73,0.3)"
                    col_v = "#3fb950" if typ=="RECETTE" else "#f85149"
                    ic  = "🟢" if typ=="RECETTE" else "🔴"
                    st.markdown(f"""
                    <div style="background:{bg}; border:1px solid {brd};
                         border-radius:10px; padding:12px; text-align:center; margin:8px 0;">
                        {ic} <span style="color:{col_v}; font-weight:700;">{mga(mnt)}</span>
                    </div>
                    """, unsafe_allow_html=True)

                if st.form_submit_button("✅ Enregistrer", use_container_width=True):
                    if not des.strip():
                        st.error("❌ Veuillez saisir une description.")
                    else:
                        conn.execute(
                            "INSERT INTO journal(date,type,description,montant) VALUES(?,?,?,?)",
                            (dat.isoformat(), typ, des, mnt)
                        )
                        conn.commit(); st.success("✅ Enregistré !"); st.rerun()

        with t_edit:
            if not df_j.empty:
                item = st.selectbox("Opération", df_j.itertuples(),
                                    format_func=lambda x:
                                    f"{'🔴' if x.type=='DEPENSE' else '🟢'} "
                                    f"{x.date[:10]} | {x.description}")
                with st.form("edit_j"):
                    e_des = st.text_input("Description", value=item.description)
                    e_mnt = st.number_input("Montant", value=int(item.montant), step=1000)
                    st.markdown("---")
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 Mettre à jour", use_container_width=True):
                        conn.execute("UPDATE journal SET description=?, montant=? WHERE id=?",
                                     (e_des, e_mnt, item.id))
                        conn.commit(); st.success("✅ Mis à jour !"); st.rerun()
                    if b2.form_submit_button("🗑️ Supprimer", use_container_width=True):
                        conn.execute("DELETE FROM journal WHERE id=?", (item.id,))
                        conn.commit(); st.warning("🗑️ Supprimé."); st.rerun()
            else:
                st.info("Aucune opération.")

    with col2:
        today = datetime.now().strftime("%Y-%m-%d")
        rec_t = pd.read_sql("SELECT SUM(montant) as v FROM journal WHERE type='RECETTE' AND date LIKE ?",
                            conn, params=(today+"%",)).v[0] or 0
        dep_t = pd.read_sql("SELECT SUM(montant) as v FROM journal WHERE type='DEPENSE' AND date LIKE ?",
                            conn, params=(today+"%",)).v[0] or 0

        kc1, kc2, kc3 = st.columns(3)
        kc1.metric("🟢 Recettes aujourd'hui", mga(rec_t))
        kc2.metric("🔴 Dépenses aujourd'hui", mga(dep_t))
        kc3.metric("📊 Solde du jour",         mga(rec_t - dep_t))

        st.markdown("<br>", unsafe_allow_html=True)

        if not df_j.empty:
            dd = df_j.drop(columns=["id"]).copy()
            dd["montant"] = dd["montant"].apply(mga)
            dd["type"]    = dd["type"].apply(
                lambda x: "🟢 RECETTE" if x=="RECETTE" else "🔴 DÉPENSE"
            )
            st.dataframe(dd, use_container_width=True, height=380)

            csv = df_j.drop(columns=["id"]).to_csv(index=False).encode("utf-8")
            st.download_button("📥 Exporter CSV", csv, "journal.csv", "text/csv",
                               use_container_width=True)


# ============================================================
# --- COMPTABILITÉ ---
# ============================================================
else:
    page_header("💰", "Comptabilité Générale", "Synthèse financière complète")

    mouv = pd.read_sql("SELECT type, (qte*pu) as montant FROM mouvements", conn)
    jour = pd.read_sql("SELECT type, montant FROM journal", conn)

    recettes = (mouv[mouv.type=='VENTE']["montant"].sum() +
                jour[jour.type=='RECETTE']["montant"].sum())
    depenses = (mouv[mouv.type=='ACHAT']["montant"].sum() +
                jour[jour.type=='DEPENSE']["montant"].sum())
    profit   = recettes - depenses

    c1, c2, c3 = st.columns(3)
    c1.metric("💚 Total Recettes", mga(recettes))
    c2.metric("❤️ Total Dépenses", mga(depenses))
    c3.metric("🏆 Profit Global",  mga(profit))

    st.markdown("<br>", unsafe_allow_html=True)

    col_chart, col_detail = st.columns([2, 1])

    with col_chart:
        st.markdown("### 📈 Évolution financière")
        m_plot = pd.read_sql(
            "SELECT substr(date,1,10) as date, (qte*pu) as montant, type FROM mouvements", conn)
        j_plot = pd.read_sql(
            "SELECT substr(date,1,10) as date, montant, type FROM journal", conn)
        td = pd.concat([m_plot, j_plot])

        if not td.empty:
            td['Recettes'] = td.apply(
                lambda x: x['montant'] if x['type'] in ['VENTE','RECETTE'] else 0, axis=1)
            td['Dépenses'] = td.apply(
                lambda x: x['montant'] if x['type'] in ['ACHAT','DEPENSE'] else 0, axis=1)
            chart = td.groupby('date')[['Recettes','Dépenses']].sum()
            st.line_chart(chart)

            st.markdown("### 📊 Solde cumulé")
            chart['Solde'] = (chart['Recettes'] - chart['Dépenses']).cumsum()
            st.area_chart(chart[['Solde']])
        else:
            st.info("Pas encore de données.")

    with col_detail:
        st.markdown("### 🏷️ Ventes par catégorie")
        vd = pd.read_sql(
            """SELECT p.categorie, SUM(m.qte*m.pu) as total
               FROM mouvements m JOIN produits p ON m.produit_id=p.id
               WHERE m.type='VENTE' GROUP BY p.categorie ORDER BY total DESC""",
            conn
        )
        if not vd.empty:
            for _, row in vd.iterrows():
                pct = (row['total'] / vd['total'].sum()) * 100
                st.markdown(f"""
                <div style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between;
                         font-size:0.85rem; margin-bottom:5px; color:#c9d1d9;">
                        <span>{row['categorie']}</span>
                        <span style="color:#58a6ff; font-weight:600;">{mga(row['total'])}</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width:{pct}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucune vente.")

        st.markdown("---")

        # Carte profit/perte
        is_profit = profit >= 0
        bg_p  = "rgba(63,185,80,0.1)"  if is_profit else "rgba(248,81,73,0.1)"
        brd_p = "rgba(63,185,80,0.3)"  if is_profit else "rgba(248,81,73,0.3)"
        col_p = "#3fb950" if is_profit else "#f85149"
        msg_p = "🎉 Vous êtes en bénéfice !" if is_profit else "⚠️ Attention, vous êtes en perte."

        st.markdown(f"""
        <div style="background:{bg_p}; border:1px solid {brd_p};
             border-radius:16px; padding:28px; text-align:center;">
            <div style="font-size:2.5rem;">{'🎉' if is_profit else '⚠️'}</div>
            <div style="color:#8b949e; font-size:0.88rem; margin-top:8px;">{msg_p}</div>
            <div style="color:{col_p}; font-size:1.7rem; font-weight:700; margin-top:8px;">
                {mga(profit)}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Exports
        all_m = pd.read_sql("SELECT * FROM mouvements", conn)
        all_j = pd.read_sql("SELECT * FROM journal", conn)
        if not all_m.empty or not all_j.empty:
            ec1, ec2 = st.columns(2)
            ec1.download_button("📥 Mouvements",
                                all_m.to_csv(index=False).encode(), "mouvements.csv",
                                "text/csv", use_container_width=True)
            ec2.download_button("📥 Journal",
                                all_j.to_csv(index=False).encode(), "journal.csv",
                                "text/csv", use_container_width=True)
