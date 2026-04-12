import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

DB = "gestion_tables_mga.db"

# ================================================================
# CONFIGURATION MOBILE
# ================================================================
st.set_page_config(
    page_title="M&M Mobile",
    layout="centered",      # ← centré pour mobile
    page_icon="🏗️",
    initial_sidebar_state="collapsed"   # ← sidebar cachée par défaut
)

# ================================================================
# CSS MOBILE MODE SOMBRE
# ================================================================
st.markdown("""
<style>
/* ==================== IMPORTS ==================== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ==================== GLOBAL MOBILE ==================== */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #0a0f1c;
    color: #e2e8f0;
}

/* Forcer le contenu centré pour mobile */
.block-container {
    padding: 1rem 0.8rem !important;
    max-width: 100% !important;
}

/* ==================== CACHER SIDEBAR SUR MOBILE ==================== */
section[data-testid="stSidebar"] {
    display: none !important;
}
/* Cacher le bouton hamburger */
button[kind="header"] {
    display: none !important;
}
header[data-testid="stHeader"] {
    display: none !important;
}

/* ==================== SCROLLBAR ==================== */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #111827; }
::-webkit-scrollbar-thumb { background: #475569; border-radius: 10px; }

/* ==================== NAVIGATION BOTTOM BAR ==================== */
.mobile-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #111827;
    border-top: 1px solid rgba(255,255,255,0.08);
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 8px 4px 12px 4px;
    z-index: 9999;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    background: rgba(17, 24, 39, 0.95);
}
.mobile-nav a {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-decoration: none;
    color: #64748b;
    font-size: 0.65rem;
    font-weight: 500;
    padding: 4px 8px;
    border-radius: 10px;
    transition: all 0.25s;
    gap: 2px;
}
.mobile-nav a:hover, .mobile-nav a.active {
    color: #a78bfa;
    background: rgba(123, 104, 238, 0.1);
}
.mobile-nav a .nav-icon {
    font-size: 1.3rem;
    line-height: 1;
}
.mobile-nav a.active .nav-icon {
    transform: scale(1.15);
}

/* Padding bottom pour ne pas cacher le contenu */
.main-content {
    padding-bottom: 80px !important;
}

/* ==================== MOBILE HEADER ==================== */
.mobile-header {
    text-align: center;
    padding: 16px 8px 20px 8px;
    border-bottom: 2px solid rgba(123, 104, 238, 0.2);
    margin-bottom: 20px;
}
.mobile-header .app-name {
    background: linear-gradient(135deg, #a78bfa, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: -0.3px;
}
.mobile-header .page-title {
    color: #94a3b8;
    font-size: 0.8rem;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

/* ==================== MOBILE KPI CARDS ==================== */
.kpi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 16px;
}
.kpi-card {
    border-radius: 14px;
    padding: 16px 14px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    transition: transform 0.2s;
}
.kpi-card:active {
    transform: scale(0.97);
}
.kpi-card .kpi-icon {
    font-size: 1.4rem;
    margin-bottom: 6px;
}
.kpi-card .kpi-value {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 2px;
}
.kpi-card .kpi-label {
    font-size: 0.7rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.kpi-card.purple {
    background: linear-gradient(135deg, #312e81, #4c1d95);
    border-color: rgba(139,92,246,0.3);
}
.kpi-card.purple .kpi-value { color: #c4b5fd; }

.kpi-card.green {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border-color: rgba(52,211,153,0.3);
}
.kpi-card.green .kpi-value { color: #6ee7b7; }

.kpi-card.blue {
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    border-color: rgba(129,140,248,0.3);
}
.kpi-card.blue .kpi-value { color: #a5b4fc; }

.kpi-card.red {
    background: linear-gradient(135deg, #7f1d1d, #991b1b);
    border-color: rgba(239,68,68,0.3);
}
.kpi-card.red .kpi-value { color: #fca5a5; }

.kpi-card.full {
    grid-column: 1 / -1;
}

/* ==================== MOBILE SECTIONS ==================== */
.section-title {
    color: #c4d0ff;
    font-size: 1rem;
    font-weight: 700;
    margin: 20px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.08);
}

/* ==================== MOBILE CARDS ==================== */
.mobile-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
    animation: fadeIn 0.3s ease-out;
}
.mobile-card .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.mobile-card .card-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: #e2e8f0;
}
.mobile-card .card-badge {
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
}
.mobile-card .card-details {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}
.mobile-card .detail-chip {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.75rem;
    color: #94a3b8;
}

/* ==================== ALERT CARDS MOBILE ==================== */
.alert-mobile {
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 8px;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 10px;
    border: 1px solid rgba(255,255,255,0.06);
}
.alert-mobile.danger {
    background: rgba(239,68,68,0.1);
    border-color: rgba(239,68,68,0.2);
}
.alert-mobile.warning {
    background: rgba(234,179,8,0.1);
    border-color: rgba(234,179,8,0.2);
}
.alert-mobile.success {
    background: rgba(34,197,94,0.1);
    border-color: rgba(34,197,94,0.2);
}
.alert-mobile .alert-icon { font-size: 1.2rem; }
.alert-mobile .alert-text { flex: 1; }
.alert-mobile .alert-text strong { color: #e2e8f0; }
.alert-mobile .alert-text small { color: #94a3b8; }

/* ==================== INPUTS MOBILE ==================== */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #1e2937 !important;
    color: #e2e8f0 !important;
    border: 1.5px solid #334155 !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    font-size: 16px !important;   /* empêche le zoom iOS */
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #7b68ee !important;
    box-shadow: 0 0 0 3px rgba(123,104,238,0.2) !important;
}
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stDateInput label {
    color: #94a3b8 !important;
    font-weight: 500;
    font-size: 0.85rem;
}
.stSelectbox > div > div {
    background: #1e2937 !important;
    border: 1.5px solid #334155 !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 16px !important;
}

/* ==================== BOUTONS MOBILE ==================== */
.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(135deg, #7b68ee, #a78bfa) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    width: 100%;
    transition: all 0.2s;
    letter-spacing: 0.3px;
}
.stButton > button:active, .stFormSubmitButton > button:active {
    transform: scale(0.97);
    box-shadow: 0 4px 16px rgba(123,104,238,0.3) !important;
}

/* ==================== TABS MOBILE ==================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #111827;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.06);
    overflow-x: auto;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: 500;
    color: #94a3b8 !important;
    font-size: 0.85rem;
    white-space: nowrap;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7b68ee, #a78bfa) !important;
    color: white !important;
    font-weight: 600;
}

/* ==================== FORM MOBILE ==================== */
div[data-testid="stForm"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 18px 16px;
}

/* ==================== DATAFRAME MOBILE ==================== */
.stDataFrame {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
    font-size: 0.8rem !important;
}

/* ==================== DIVIDER ==================== */
hr {
    border-color: rgba(255,255,255,0.06) !important;
}

/* ==================== DOWNLOAD BUTTON ==================== */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1e2937, #334155) !important;
    border: 1px solid #475569 !important;
    color: #c4b5fd !important;
    border-radius: 12px !important;
}

/* ==================== STOCK LIST MOBILE ==================== */
.stock-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 14px;
    background: #111827;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    margin-bottom: 8px;
    transition: all 0.2s;
}
.stock-item:active {
    background: #1e2937;
}
.stock-item .item-info {
    flex: 1;
}
.stock-item .item-name {
    font-weight: 600;
    font-size: 0.88rem;
    color: #e2e8f0;
    margin-bottom: 2px;
}
.stock-item .item-code {
    font-size: 0.72rem;
    color: #64748b;
    font-family: monospace;
}
.stock-item .item-stock {
    text-align: right;
}
.stock-item .stock-count {
    font-size: 1.1rem;
    font-weight: 700;
}
.stock-item .stock-label {
    font-size: 0.65rem;
    color: #64748b;
    text-transform: uppercase;
}

/* ==================== TRANSACTION LIST ==================== */
.transaction-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    background: #111827;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    margin-bottom: 8px;
}
.transaction-item .tx-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.transaction-item .tx-icon.income {
    background: rgba(34,197,94,0.15);
}
.transaction-item .tx-icon.expense {
    background: rgba(239,68,68,0.15);
}
.transaction-item .tx-details {
    flex: 1;
    min-width: 0;
}
.transaction-item .tx-desc {
    font-weight: 600;
    font-size: 0.85rem;
    color: #e2e8f0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.transaction-item .tx-date {
    font-size: 0.72rem;
    color: #64748b;
}
.transaction-item .tx-amount {
    font-weight: 700;
    font-size: 0.9rem;
    text-align: right;
    flex-shrink: 0;
}

/* ==================== PROGRESS BAR ==================== */
.progress-bar-bg {
    background: #1e2937;
    border-radius: 10px;
    height: 6px;
    overflow: hidden;
    margin-top: 4px;
}
.progress-bar-fill {
    background: linear-gradient(90deg, #7b68ee, #a78bfa);
    height: 100%;
    border-radius: 10px;
}

/* ==================== ANIMATIONS ==================== */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.kpi-card, .mobile-card, .stock-item, .transaction-item {
    animation: fadeIn 0.3s ease-out;
}

/* ==================== EMPTY STATE ==================== */
.empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #64748b;
}
.empty-state .empty-icon {
    font-size: 3rem;
    margin-bottom: 12px;
    opacity: 0.6;
}
.empty-state h4 {
    color: #94a3b8 !important;
    margin-bottom: 8px;
}
.empty-state p {
    font-size: 0.85rem;
    color: #64748b;
}
</style>
""", unsafe_allow_html=True)


# ================================================================
# UTILS
# ================================================================
def mga(x):
    return f"{int(x or 0):,}".replace(",", " ") + " Ar"

def mga_short(x):
    val = int(x or 0)
    if val >= 1_000_000:
        return f"{val/1_000_000:.1f}M Ar"
    elif val >= 1_000:
        return f"{val/1_000:.0f}K Ar"
    return f"{val} Ar"

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
# LISTES
# ================================================================
LISTE_PIEDS = ["/U", "/V", "/X", "/K", "/PLIABLE", "/TABOURET CARRE", "/TABOURET CERCLE"]
LISTE_COULEURS = [
    "/BLANC UNIS", "/NOIR UNIS", "/GRIS MARBRE",
    "#1023", "#1025", "#805", "#806", "#506",
    "#16854", "#16855", "#1010", "#8042", "#8052",
    "#932", "#809", "#308 BM", "#7058", "#76-1"
]

# ================================================================
# NAVIGATION MOBILE (via query params)
# ================================================================
PAGES = {
    "home": {"icon": "🏠", "label": "Accueil"},
    "produits": {"icon": "📦", "label": "Produits"},
    "entrees": {"icon": "📥", "label": "Entrées"},
    "ventes": {"icon": "📤", "label": "Ventes"},
    "journal": {"icon": "📒", "label": "Journal"},
    "compta": {"icon": "💰", "label": "Compta"},
}

# Récupérer la page courante
query_params = st.query_params
current_page = query_params.get("page", "home")
if current_page not in PAGES:
    current_page = "home"


def mobile_header(title):
    st.markdown(f"""
    <div class="mobile-header">
        <div class="app-name">🏗️ M&M</div>
        <div class="page-title">{title}</div>
    </div>
    """, unsafe_allow_html=True)


def section_title(icon, title):
    st.markdown(f"""
    <div class="section-title">{icon} {title}</div>
    """, unsafe_allow_html=True)


def render_bottom_nav():
    nav_html = '<div class="mobile-nav">'
    for key, info in PAGES.items():
        active = "active" if key == current_page else ""
        nav_html += f"""
        <a href="?page={key}" class="{active}" target="_self">
            <span class="nav-icon">{info['icon']}</span>
            {info['label']}
        </a>
        """
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)


# Afficher la barre de navigation en bas
render_bottom_nav()

# Wrapper principal avec padding bottom
st.markdown('<div class="main-content">', unsafe_allow_html=True)


# ================================================================
# 🏠 ACCUEIL / TABLEAU DE BORD
# ================================================================
if current_page == "home":
    mobile_header("Tableau de bord")

    prod = pd.read_sql("SELECT * FROM produits", conn)
    valeur_stock = (prod["stock"] * prod["prix_vente"]).sum() if not prod.empty else 0
    total_produits = len(prod)

    mois = datetime.now().strftime("%Y-%m") + "%"
    today = datetime.now().strftime("%Y-%m-%d") + "%"

    v_prod = pd.read_sql(
        "SELECT COALESCE(SUM(qte*pu),0) as v FROM mouvements WHERE type='VENTE' AND date LIKE ?",
        conn, params=(mois,)
    ).v[0]
    r_jour = pd.read_sql(
        "SELECT COALESCE(SUM(montant),0) as v FROM journal WHERE type='RECETTE' AND date LIKE ?",
        conn, params=(mois,)
    ).v[0]
    recettes_mois = v_prod + r_jour

    a_prod = pd.read_sql(
        "SELECT COALESCE(SUM(qte*pu),0) as v FROM mouvements WHERE type='ACHAT' AND date LIKE ?",
        conn, params=(mois,)
    ).v[0]
    d_jour = pd.read_sql(
        "SELECT COALESCE(SUM(montant),0) as v FROM journal WHERE type='DEPENSE' AND date LIKE ?",
        conn, params=(mois,)
    ).v[0]
    depenses_mois = a_prod + d_jour
    benefice = recettes_mois - depenses_mois

    # Ventes du jour
    v_today = pd.read_sql(
        "SELECT COALESCE(SUM(qte*pu),0) as v FROM mouvements WHERE type='VENTE' AND date LIKE ?",
        conn, params=(today,)
    ).v[0]
    r_today = pd.read_sql(
        "SELECT COALESCE(SUM(montant),0) as v FROM journal WHERE type='RECETTE' AND date LIKE ?",
        conn, params=(today,)
    ).v[0]
    ventes_today = v_today + r_today

    # KPI Grid
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card purple">
            <div class="kpi-icon">💎</div>
            <div class="kpi-value">{mga_short(valeur_stock)}</div>
            <div class="kpi-label">Valeur stock</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-icon">📈</div>
            <div class="kpi-value">{mga_short(recettes_mois)}</div>
            <div class="kpi-label">Recettes mois</div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-icon">🛒</div>
            <div class="kpi-value">{mga_short(ventes_today)}</div>
            <div class="kpi-label">Ventes aujourd'hui</div>
        </div>
        <div class="kpi-card {'green' if benefice >= 0 else 'red'}">
            <div class="kpi-icon">{'🏆' if benefice >= 0 else '⚠️'}</div>
            <div class="kpi-value">{mga_short(benefice)}</div>
            <div class="kpi-label">Bénéfice net</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Alertes stock
    if not prod.empty:
        low_items = prod[prod["stock"] <= 3].sort_values("stock")
        if not low_items.empty:
            section_title("⚠️", "Alertes stock")
            for _, row in low_items.head(5).iterrows():
                cls = "danger" if row["stock"] <= 0 else "warning"
                emoji = "🔴" if row["stock"] <= 0 else "🟡"
                st.markdown(f"""
                <div class="alert-mobile {cls}">
                    <span class="alert-icon">{emoji}</span>
                    <div class="alert-text">
                        <strong>{row['nom']}</strong><br>
                        <small>Stock: {int(row['stock'])} unité(s)</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Dernières ventes
    last_sales = pd.read_sql(
        """SELECT m.date, p.nom, m.qte, (m.qte*m.pu) as total
           FROM mouvements m JOIN produits p ON m.produit_id=p.id
           WHERE m.type='VENTE' ORDER BY m.date DESC LIMIT 5""",
        conn
    )
    if not last_sales.empty:
        section_title("📤", "Dernières ventes")
        for _, row in last_sales.iterrows():
            dt = pd.to_datetime(row['date']).strftime("%d/%m %H:%M")
            st.markdown(f"""
            <div class="transaction-item">
                <div class="tx-icon income">📤</div>
                <div class="tx-details">
                    <div class="tx-desc">{row['nom']}</div>
                    <div class="tx-date">{dt} · {int(row['qte'])} unité(s)</div>
                </div>
                <div class="tx-amount" style="color: #6ee7b7;">
                    +{mga_short(row['total'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Dernières dépenses journal
    last_deps = pd.read_sql(
        "SELECT date, description, montant FROM journal "
        "WHERE type='DEPENSE' ORDER BY date DESC LIMIT 3", conn
    )
    if not last_deps.empty:
        section_title("🔴", "Dernières dépenses")
        for _, row in last_deps.iterrows():
            dt = row['date'][:10]
            st.markdown(f"""
            <div class="transaction-item">
                <div class="tx-icon expense">💸</div>
                <div class="tx-details">
                    <div class="tx-desc">{row['description']}</div>
                    <div class="tx-date">{dt}</div>
                </div>
                <div class="tx-amount" style="color: #fca5a5;">
                    -{mga_short(row['montant'])}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ================================================================
# 📦 PRODUITS
# ================================================================
elif current_page == "produits":
    mobile_header("Produits")

    df = pd.read_sql("SELECT * FROM produits", conn)

    tab_list, tab_add, tab_edit = st.tabs(["📋 Liste", "➕ Ajouter", "✏️ Modifier"])

    with tab_list:
        if not df.empty:
            # Stats rapides
            st.markdown(f"""
            <div class="kpi-grid">
                <div class="kpi-card purple">
                    <div class="kpi-value">{len(df)}</div>
                    <div class="kpi-label">Produits</div>
                </div>
                <div class="kpi-card green">
                    <div class="kpi-value">{int(df['stock'].sum())}</div>
                    <div class="kpi-label">En stock</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Recherche
            search = st.text_input("🔍", placeholder="Rechercher...",
                                   label_visibility="collapsed")
            cat_filter = st.selectbox(
                "Catégorie",
                ["Toutes"] + sorted(df["categorie"].dropna().unique().tolist()),
                label_visibility="collapsed"
            )

            df_f = df.copy()
            if cat_filter != "Toutes":
                df_f = df_f[df_f["categorie"] == cat_filter]
            if search:
                mask = (
                    df_f["nom"].str.contains(search, case=False, na=False) |
                    df_f["code"].str.contains(search, case=False, na=False)
                )
                df_f = df_f[mask]

            # Liste de produits
            for _, row in df_f.iterrows():
                stock = int(row['stock'])
                if stock <= 0:
                    color = "#fca5a5"
                elif stock <= 3:
                    color = "#fde047"
                else:
                    color = "#6ee7b7"

                st.markdown(f"""
                <div class="stock-item">
                    <div class="item-info">
                        <div class="item-name">{row['nom']}</div>
                        <div class="item-code">{row['code']}</div>
                    </div>
                    <div class="item-stock">
                        <div class="stock-count" style="color: {color};">{stock}</div>
                        <div class="stock-label">en stock</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📦</div>
                <h4>Aucun produit</h4>
                <p>Ajoutez votre premier produit</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_add:
        st.markdown("""
        <div class="mobile-card">
            💡 Le <strong>nom</strong> et le <strong>code</strong> sont générés automatiquement.
        </div>
        """, unsafe_allow_html=True)

        with st.form("add_prod_m", clear_on_submit=True):
            cat = st.selectbox("📂 Catégorie",
                               ["TABLE", "CHAISE", "BUREAU", "ETAGERE", "AUTRE"])
            coul = st.selectbox("�� Couleur", LISTE_COULEURS)
            pieds = st.selectbox("🦶 Forme pieds", LISTE_PIEDS)

            c1, c2 = st.columns(2)
            long = c1.number_input("📏 Long. (cm)", 0, step=5)
            larg = c2.number_input("📐 Larg. (cm)", 0, step=5)
            haut = st.number_input("📐 Haut. (cm)", 0, step=5)

            c1, c2 = st.columns(2)
            pa = c1.number_input("💰 P. Achat", 0, step=1000)
            pv = c2.number_input("💲 P. Vente", 0, step=1000)
            stock = st.number_input("📦 Stock initial", 0)

            if st.form_submit_button("✅ Enregistrer", use_container_width=True):
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
                    st.success(f"✅ **{nom_auto}** créé !")
                    st.balloons()
                    st.rerun()
                except:
                    st.error("❌ Code déjà existant.")

    with tab_edit:
        if not df.empty:
            p_edit = st.selectbox(
                "Produit",
                df.itertuples(),
                format_func=lambda x: f"{x.nom} ({x.stock})",
                label_visibility="collapsed"
            )

            st.markdown(f"""
            <div class="mobile-card">
                <div class="card-header">
                    <span class="card-title">{p_edit.nom}</span>
                </div>
                <div class="card-details">
                    <span class="detail-chip">📦 Stock: {p_edit.stock}</span>
                    <span class="detail-chip">💲 {mga(p_edit.prix_vente)}</span>
                    <span class="detail-chip">🏷️ {p_edit.code}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("edit_prod_m"):
                n_pv = st.number_input("💲 Prix Vente",
                                       value=int(p_edit.prix_vente), step=1000)
                n_stock = st.number_input("📦 Stock",
                                          value=int(p_edit.stock))

                c1, c2 = st.columns(2)
                if c1.form_submit_button("💾 Sauver", use_container_width=True):
                    conn.execute(
                        "UPDATE produits SET prix_vente=?, stock=? WHERE id=?",
                        (n_pv, n_stock, p_edit.id)
                    )
                    conn.commit()
                    st.success("✅ Mis à jour !")
                    st.rerun()
                if c2.form_submit_button("🗑️ Suppr.", use_container_width=True):
                    conn.execute("DELETE FROM produits WHERE id=?", (p_edit.id,))
                    conn.commit()
                    st.warning("🗑️ Supprimé.")
                    st.rerun()
        else:
            st.info("Aucun produit.")


# ================================================================
# 📥 ENTRÉES STOCK
# ================================================================
elif current_page == "entrees":
    mobile_header("Entrées Stock")

    prod = pd.read_sql("SELECT id, code, nom, stock FROM produits", conn)
    four = pd.read_sql("SELECT * FROM fournisseurs", conn)

    tab_form, tab_hist = st.tabs(["📝 Nouvelle entrée", "📜 Historique"])

    with tab_form:
        with st.form("entree_m", clear_on_submit=True):
            if not prod.empty:
                p = st.selectbox(
                    "📦 Produit", prod.itertuples(),
                    format_func=lambda x: f"{x.nom} (Stock: {x.stock})"
                )
            else:
                st.warning("Aucun produit.")
                p = None

            if not four.empty:
                f = st.selectbox("🏭 Fournisseur", four.itertuples(),
                                 format_func=lambda x: x.nom)
                f_nom = f.nom
            else:
                f_nom = st.text_input("🏭 Fournisseur")

            c1, c2 = st.columns(2)
            qte = c1.number_input("📊 Qté", 1, step=1)
            pu = c2.number_input("💲 PU Achat", 0, step=1000)

            total = qte * pu
            st.markdown(f"""
            <div class="mobile-card" style="text-align:center;">
                <span style="color: #6ee7b7; font-weight: 700; font-size: 1.1rem;">
                    Total : {mga(total)}
                </span>
            </div>
            """, unsafe_allow_html=True)

            if st.form_submit_button("✅ Valider", use_container_width=True):
                if p is not None:
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
                    st.success(f"✅ +{qte} ajouté(s) !")
                    st.rerun()

    with tab_hist:
        achats = pd.read_sql(
            """SELECT m.date, p.nom, m.qte, (m.qte*m.pu) as total, m.tiers
               FROM mouvements m JOIN produits p ON m.produit_id=p.id
               WHERE m.type='ACHAT' ORDER BY m.date DESC LIMIT 20""",
            conn
        )
        if not achats.empty:
            for _, row in achats.iterrows():
                dt = pd.to_datetime(row['date']).strftime("%d/%m %H:%M")
                st.markdown(f"""
                <div class="transaction-item">
                    <div class="tx-icon expense">📥</div>
                    <div class="tx-details">
                        <div class="tx-desc">{row['nom']}</div>
                        <div class="tx-date">{dt} · {int(row['qte'])} u. · {row['tiers'] or '—'}</div>
                    </div>
                    <div class="tx-amount" style="color: #fca5a5;">
                        -{mga_short(row['total'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <h4>Aucun achat</h4>
            </div>
            """, unsafe_allow_html=True)


# ================================================================
# 📤 VENTES
# ================================================================
elif current_page == "ventes":
    mobile_header("Ventes")

    prod = pd.read_sql("SELECT * FROM produits WHERE stock>0", conn)
    cli = pd.read_sql("SELECT * FROM clients", conn)

    tab_form, tab_hist = st.tabs(["🛒 Nouvelle vente", "📜 Historique"])

    with tab_form:
        if not prod.empty:
            with st.form("vente_m", clear_on_submit=True):
                p = st.selectbox(
                    "📦 Produit", prod.itertuples(),
                    format_func=lambda x: f"{x.nom} (Stock: {x.stock})"
                )
                if not cli.empty:
                    c = st.selectbox("👤 Client", cli.itertuples(),
                                     format_func=lambda x: x.nom)
                    c_nom = c.nom
                else:
                    c_nom = st.text_input("👤 Client")

                c1, c2 = st.columns(2)
                qte = c1.number_input("📊 Qté", 1, max_value=int(p.stock))
                pu = c2.number_input("💲 Prix", int(p.prix_vente), step=1000)

                total_v = qte * pu
                marge = (pu - (p.prix_achat or 0)) * qte

                st.markdown(f"""
                <div class="kpi-grid">
                    <div class="kpi-card blue">
                        <div class="kpi-value">{mga_short(total_v)}</div>
                        <div class="kpi-label">Total</div>
                    </div>
                    <div class="kpi-card {'green' if marge >= 0 else 'red'}">
                        <div class="kpi-value">{mga_short(marge)}</div>
                        <div class="kpi-label">Marge</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.form_submit_button("✅ Vendre", use_container_width=True):
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
                    st.success(f"✅ Réf: `{ref}`")
                    st.balloons()
                    st.rerun()
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📦</div>
                <h4>Stock vide</h4>
                <p>Réapprovisionnez via 📥 Entrées</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_hist:
        ventes = pd.read_sql(
            """SELECT m.date, m.ref, p.nom, m.qte, (m.qte*m.pu) as total, m.tiers
               FROM mouvements m JOIN produits p ON m.produit_id=p.id
               WHERE m.type='VENTE' ORDER BY m.date DESC LIMIT 20""",
            conn
        )
        if not ventes.empty:
            for _, row in ventes.iterrows():
                dt = pd.to_datetime(row['date']).strftime("%d/%m %H:%M")
                st.markdown(f"""
                <div class="transaction-item">
                    <div class="tx-icon income">📤</div>
                    <div class="tx-details">
                        <div class="tx-desc">{row['nom']}</div>
                        <div class="tx-date">{dt} · {row['ref']} · {row['tiers'] or '—'}</div>
                    </div>
                    <div class="tx-amount" style="color: #6ee7b7;">
                        +{mga_short(row['total'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <h4>Aucune vente</h4>
            </div>
            """, unsafe_allow_html=True)


# ================================================================
# 📒 JOURNALIER
# ================================================================
elif current_page == "journal":
    mobile_header("Journal")

    df_j = pd.read_sql(
        "SELECT id, date, type, description, montant "
        "FROM journal ORDER BY date DESC", conn
    )

    # KPI du jour
    today = datetime.now().strftime("%Y-%m-%d") + "%"
    rec_t = pd.read_sql(
        "SELECT COALESCE(SUM(montant),0) as v FROM journal WHERE type='RECETTE' AND date LIKE ?",
        conn, params=(today,)
    ).v[0]
    dep_t = pd.read_sql(
        "SELECT COALESCE(SUM(montant),0) as v FROM journal WHERE type='DEPENSE' AND date LIKE ?",
        conn, params=(today,)
    ).v[0]

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card green">
            <div class="kpi-icon">🟢</div>
            <div class="kpi-value">{mga_short(rec_t)}</div>
            <div class="kpi-label">Recettes jour</div>
        </div>
        <div class="kpi-card red">
            <div class="kpi-icon">🔴</div>
            <div class="kpi-value">{mga_short(dep_t)}</div>
            <div class="kpi-label">Dépenses jour</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_add, tab_list, tab_edit = st.tabs(["➕ Ajouter", "📋 Liste", "✏️ Modifier"])

    with tab_add:
        with st.form("add_j_m", clear_on_submit=True):
            typ = st.selectbox(
                "Type", ["DEPENSE", "RECETTE"],
                format_func=lambda x: f"{'🔴 Dépense' if x == 'DEPENSE' else '🟢 Recette'}"
            )
            des = st.text_input("📝 Description")
            mnt = st.number_input("💲 Montant (Ar)", 0, step=1000)
            dat = st.date_input("📅 Date", datetime.now())

            if mnt > 0:
                color = "rgba(34,197,94,0.1)" if typ == "RECETTE" else "rgba(239,68,68,0.1)"
                txt = "#6ee7b7" if typ == "RECETTE" else "#fca5a5"
                icon = "🟢" if typ == "RECETTE" else "🔴"
                st.markdown(f"""
                <div class="mobile-card" style="text-align:center;background:{color};">
                    <span style="color:{txt};font-weight:700;">{icon} {mga(mnt)}</span>
                </div>
                """, unsafe_allow_html=True)

            if st.form_submit_button("✅ Enregistrer", use_container_width=True):
                if des.strip():
                    conn.execute(
                        "INSERT INTO journal(date,type,description,montant) VALUES (?,?,?,?)",
                        (dat.isoformat(), typ, des, mnt)
                    )
                    conn.commit()
                    st.success("✅ Enregistré !")
                    st.rerun()
                else:
                    st.error("❌ Description requise.")

    with tab_list:
        if not df_j.empty:
            for _, row in df_j.head(20).iterrows():
                is_income = row['type'] == 'RECETTE'
                icon_cls = "income" if is_income else "expense"
                icon = "🟢" if is_income else "🔴"
                color = "#6ee7b7" if is_income else "#fca5a5"
                sign = "+" if is_income else "-"

                st.markdown(f"""
                <div class="transaction-item">
                    <div class="tx-icon {icon_cls}">{icon}</div>
                    <div class="tx-details">
                        <div class="tx-desc">{row['description']}</div>
                        <div class="tx-date">{row['date'][:10]}</div>
                    </div>
                    <div class="tx-amount" style="color: {color};">
                        {sign}{mga_short(row['montant'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Export
            csv = df_j.drop(columns=["id"]).to_csv(index=False).encode("utf-8")
            st.download_button("📥 Exporter CSV", csv, "journal.csv",
                               "text/csv", use_container_width=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <h4>Aucune opération</h4>
            </div>
            """, unsafe_allow_html=True)

    with tab_edit:
        if not df_j.empty:
            item = st.selectbox(
                "Opération",
                df_j.itertuples(),
                format_func=lambda x: (
                    f"{'🔴' if x.type == 'DEPENSE' else '🟢'} "
                    f"{x.date[:10]} | {x.description}"
                ),
                label_visibility="collapsed"
            )

            with st.form("edit_j_m"):
                e_des = st.text_input("📝 Description", value=item.description)
                e_mnt = st.number_input("💲 Montant", value=int(item.montant), step=1000)

                c1, c2 = st.columns(2)
                if c1.form_submit_button("💾 Sauver", use_container_width=True):
                    conn.execute(
                        "UPDATE journal SET description=?, montant=? WHERE id=?",
                        (e_des, e_mnt, item.id)
                    )
                    conn.commit()
                    st.success("✅ Mis à jour !")
                    st.rerun()
                if c2.form_submit_button("🗑️ Suppr.", use_container_width=True):
                    conn.execute("DELETE FROM journal WHERE id=?", (item.id,))
                    conn.commit()
                    st.warning("🗑️ Supprimé.")
                    st.rerun()
        else:
            st.info("Aucune opération.")


# ================================================================
# 💰 COMPTABILITÉ
# ================================================================
elif current_page == "compta":
    mobile_header("Comptabilité")

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
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card green">
            <div class="kpi-icon">💚</div>
            <div class="kpi-value">{mga_short(recettes)}</div>
            <div class="kpi-label">Recettes</div>
        </div>
        <div class="kpi-card red">
            <div class="kpi-icon">❤️</div>
            <div class="kpi-value">{mga_short(depenses)}</div>
            <div class="kpi-label">Dépenses</div>
        </div>
        <div class="kpi-card {'green' if profit >= 0 else 'red'} full">
            <div class="kpi-icon">{'🏆' if profit >= 0 else '⚠️'}</div>
            <div class="kpi-value" style="font-size: 1.4rem;">{mga(profit)}</div>
            <div class="kpi-label">{'Bénéfice' if profit >= 0 else 'Perte'} Global</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Graphique
    section_title("📈", "Évolution")

    m_plot = pd.read_sql(
        "SELECT substr(date,1,10) as date, (qte*pu) as montant, type FROM mouvements",
        conn
    )
    j_plot = pd.read_sql(
        "SELECT substr(date,1,10) as date, montant, type FROM journal", conn
    )
    total_data = pd.concat([m_plot, j_plot])

    if not total_data.empty:
        total_data['Recettes'] = total_data.apply(
            lambda x: x['montant'] if x['type'] in ['VENTE', 'RECETTE'] else 0, axis=1
        )
        total_data['Dépenses'] = total_data.apply(
            lambda x: x['montant'] if x['type'] in ['ACHAT', 'DEPENSE'] else 0, axis=1
        )
        chart_data = total_data.groupby('date')[['Recettes', 'Dépenses']].sum()
        st.line_chart(chart_data, height=250)

        section_title("📊", "Solde cumulé")
        chart_data['Solde'] = (chart_data['Recettes'] - chart_data['Dépenses']).cumsum()
        st.area_chart(chart_data[['Solde']], height=200)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📊</div>
            <h4>Pas de données</h4>
        </div>
        """, unsafe_allow_html=True)

    # Répartition par catégorie
    ventes_detail = pd.read_sql(
        """SELECT p.categorie, SUM(m.qte*m.pu) as total
           FROM mouvements m JOIN produits p ON m.produit_id=p.id
           WHERE m.type='VENTE' GROUP BY p.categorie
           ORDER BY total DESC""",
        conn
    )
    if not ventes_detail.empty:
        section_title("🏷️", "Par catégorie")
        total_v = ventes_detail['total'].sum()
        for _, row in ventes_detail.iterrows():
            pct = (row['total'] / total_v) * 100 if total_v > 0 else 0
            st.markdown(f"""
            <div style="margin-bottom: 14px;">
                <div style="display:flex; justify-content:space-between;
                     font-size:0.85rem; margin-bottom:4px;">
                    <span style="color:#cbd5e1;">{row['categorie']}</span>
                    <span style="color:#a78bfa; font-weight:600;">
                        {mga_short(row['total'])}
                    </span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width:{pct}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Export
    section_title("📥", "Exporter")
    all_mouv = pd.read_sql("SELECT * FROM mouvements", conn)
    all_jour = pd.read_sql("SELECT * FROM journal", conn)

    if not all_mouv.empty:
        csv_m = all_mouv.to_csv(index=False).encode("utf-8")
        st.download_button("📦 Mouvements", csv_m, "mouvements.csv",
                           "text/csv", use_container_width=True)
    if not all_jour.empty:
        csv_j = all_jour.to_csv(index=False).encode("utf-8")
        st.download_button("📒 Journal", csv_j, "journal.csv",
                           "text/csv", use_container_width=True)


# Fermer le wrapper
st.markdown('</div>', unsafe_allow_html=True)
