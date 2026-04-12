import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

DB = "gestion_tables_mga.db"

# ==================== CONFIGURATION MOBILE ====================
st.set_page_config(
    page_title="M&M Mobile",
    layout="wide",  # On gère le responsive via CSS
    page_icon="📱",
    initial_sidebar_state="collapsed"  # Sidebar cachée par défaut sur mobile
)

# ==================== CSS RESPONSIVE (MOBILE + DESKTOP) ====================
st.markdown("""
<style>
    /* ===== VARIABLES COULEURS ===== */
    :root {
        --bg-primary: #0a0f1c;
        --bg-secondary: #111827;
        --bg-card: #1e293b;
        --accent: #8b5cf6;
        --accent-light: #a78bfa;
        --text: #f1f5f9;
        --text-muted: #94a3b8;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #f43f5e;
    }

    /* ===== BASE ===== */
    .stApp {
        background: var(--bg-primary);
        padding-bottom: 80px; /* Espace pour bottom nav */
    }
    
    /* ===== NAVIGATION MOBILE (Bottom Bar) ===== */
    @media (max-width: 768px) {
        /* Cacher la sidebar sur mobile */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Bottom Navigation Bar */
        .mobile-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(17, 24, 39, 0.95);
            backdrop-filter: blur(20px);
            border-top: 1px solid rgba(255,255,255,0.1);
            padding: 8px 0;
            z-index: 9999;
            display: flex;
            justify-content: space-around;
            align-items: center;
            height: 65px;
        }
        
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 4px 12px;
            color: var(--text-muted);
            font-size: 0.7rem;
            text-decoration: none;
            transition: all 0.2s;
            border: none;
            background: transparent;
            cursor: pointer;
        }
        
        .nav-item.active {
            color: var(--accent-light);
        }
        
        .nav-item .icon {
            font-size: 1.4rem;
            margin-bottom: 2px;
        }
        
        /* Cards tactiles larges */
        .touch-card {
            background: var(--bg-card);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 12px;
            touch-action: manipulation;
            min-height: 44px; /* Zone de touch minimum */
        }
        
        /* Boutons grosses tailles */
        .stButton > button {
            width: 100% !important;
            padding: 16px !important;
            font-size: 1.1rem !important;
            border-radius: 12px !important;
            background: linear-gradient(135deg, #7c3aed, #8b5cf6) !important;
            border: none !important;
            color: white !important;
            font-weight: 600 !important;
            margin: 8px 0 !important;
            min-height: 56px;
        }
        
        /* Inputs plus grands pour doigts */
        .stTextInput input, .stNumberInput input, .stSelectbox > div > div {
            min-height: 50px !important;
            font-size: 16px !important; /* Empêche le zoom iOS */
        }
        
        /* Titres plus compacts */
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        /* Métriques empilées */
        div[data-testid="stMetric"] {
            padding: 16px !important;
            margin-bottom: 8px !important;
        }
        
        /* Tables scrollables horizontalement */
        .stDataFrame {
            overflow-x: auto !important;
            display: block !important;
        }
        
        /* Floating Action Button pour ajout rapide */
        .fab {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #8b5cf6, #a78bfa);
            color: white;
            border: none;
            font-size: 28px;
            box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);
            z-index: 9998;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
    }

    /* ===== DESKTOP (Sidebar visible) ===== */
    @media (min-width: 769px) {
        .mobile-nav { display: none !important; }
        .fab { display: none !important; }
        
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
        }
    }

    /* ===== STYLES COMMUNS ===== */
    .stApp {
        background: var(--bg-primary);
        color: var(--text);
    }
    
    .metric-card {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 16px;
        border-left: 4px solid var(--accent);
        margin-bottom: 12px;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text);
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Formulaires */
    .stForm {
        background: var(--bg-card);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Success/Error colors */
    .stSuccess { border-left-color: var(--success) !important; }
    .stError { border-left-color: var(--danger) !important; }
    .stWarning { border-left-color: var(--warning) !important; }
    
    /* Hide default multiselect clear buttons on mobile (too small) */
    @media (max-width: 768px) {
        [data-testid="stMultiSelect"] span[role="button"] {
            min-width: 44px;
            min-height: 44px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== UTILS & DB ====================
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
            forme_pieds TEXT, prix_achat INTEGER, prix_vente INTEGER, stock INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY, nom TEXT, tel TEXT);
        CREATE TABLE IF NOT EXISTS fournisseurs(id INTEGER PRIMARY KEY, nom TEXT, tel TEXT);
        CREATE TABLE IF NOT EXISTS mouvements(
            id INTEGER PRIMARY KEY, date TEXT, produit_id INTEGER, type TEXT,
            qte INTEGER, pu INTEGER, tiers TEXT, ref TEXT
        );
        CREATE TABLE IF NOT EXISTS journal(
            id INTEGER PRIMARY KEY, date TEXT, type TEXT, description TEXT, montant INTEGER
        );
    """)
    try:
        c.execute("ALTER TABLE produits ADD COLUMN forme_pieds TEXT")
    except:
        pass
    c.commit()

init_db()
conn = get_conn()

LISTE_PIEDS = ["/U", "/V", "/X", "/K", "/PLIABLE", "/TABOURET CARRE", "/TABOURET CERCLE"]
LISTE_COULEURS = [
    "/BLANC UNIS", "/NOIR UNIS", "/GRIS MARBRE", "#1023", "#1025", "#805", "#806", "#506",
    "#16854", "#16855", "#1010", "#8042", "#8052", "#932", "#809", "#308 BM", "#7058", "#76-1"
]

# ==================== NAVIGATION STATE ====================
if "mobile_page" not in st.session_state:
    st.session_state.mobile_page = "dashboard"

# ==================== HEADER MOBILE ====================
def mobile_header(title, subtitle=""):
    st.markdown(f"""
    <div style="padding: 16px 0; border-bottom: 2px solid rgba(139, 92, 246, 0.3); margin-bottom: 16px;">
        <h1 style="margin: 0; font-size: 1.4rem; color: #e2e8f0;">{title}</h1>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.9rem;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== BOTTOM NAVIGATION COMPONENT ====================
def render_bottom_nav():
    pages = {
        "dashboard": ("🏠", "Accueil"),
        "vente": ("🛒", "Vendre"),
        "stock": ("📦", "Stock"),
        "ajout": ("➕", "Ajout"),
        "compta": ("💰", "Compta")
    }
    
    nav_html = '<div class="mobile-nav">'
    for key, (icon, label) in pages.items():
        active = "active" if st.session_state.mobile_page == key else ""
        # Utilisation de boutons Streamlit cachés pour la navigation
        nav_html += f"""
        <div class="nav-item {active}" onclick="window.location.href='?page={key}'">
            <div class="icon">{icon}</div>
            <div>{label}</div>
        </div>
        """
    nav_html += '</div>'
    
    st.markdown(nav_html, unsafe_allow_html=True)
    
    # Gestion de la navigation via query params (pour éviter les problèmes de rerender)
    query_params = st.query_params
    if "page" in query_params:
        st.session_state.mobile_page = query_params["page"]
        st.query_params.clear()

# ==================== PAGE: DASHBOARD (ACCUEIL) ====================
def page_dashboard():
    mobile_header("Tableau de Bord", "Vue d'ensemble")
    
    # KPIs en grille 2x2 sur mobile
    prod = pd.read_sql("SELECT * FROM produits", conn)
    valeur_stock = (prod["stock"] * prod["prix_vente"]).sum()
    
    mois_actuel = datetime.now().strftime("%Y-%m") + "%"
    ventes_mois = pd.read_sql(
        "SELECT SUM(qte*pu) as val FROM mouvements WHERE type='VENTE' AND date LIKE ?",
        conn, params=(mois_actuel,)
    ).val[0] or 0
    
    recettes_jour = pd.read_sql(
        "SELECT SUM(montant) as val FROM journal WHERE type='RECETTE' AND date LIKE ?",
        conn, params=(datetime.now().strftime("%Y-%m-%d")+"%",)
    ).val[0] or 0
    
    # Grille responsive
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #8b5cf6;">
            <div class="metric-label">Valeur Stock</div>
            <div class="metric-value" style="font-size: 1.2rem;">{mga(valeur_stock)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #10b981;">
            <div class="metric-label">Ventes Mois</div>
            <div class="metric-value" style="font-size: 1.2rem;">{mga(ventes_mois)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Alertes stock critique (simplifié)
    st.markdown("### ⚠️ Alertes")
    low_stock = prod[prod["stock"] <= 3]
    if not low_stock.empty:
        for _, row in low_stock.head(3).iterrows():
            color = "#f43f5e" if row["stock"] <= 0 else "#f59e0b"
            emoji = "🔴" if row["stock"] <= 0 else "🟡"
            st.markdown(f"""
            <div style="background: rgba(0,0,0,0.3); border-left: 4px solid {color}; 
                 padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                <strong>{emoji} {row['nom'][:20]}</strong><br>
                <span style="color: #94a3b8; font-size: 0.85rem;">
                    Stock: {int(row['stock'])} | Code: {row['code']}
                </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Tous les stocks sont OK")
    
    # Actions rapides
    st.markdown("### ⚡ Actions rapides")
    a1, a2 = st.columns(2)
    with a1:
        if st.button("🛒 Nouvelle Vente", use_container_width=True):
            st.session_state.mobile_page = "vente"
            st.rerun()
    with a2:
        if st.button("📥 Entrée Stock", use_container_width=True):
            st.session_state.mobile_page = "stock"

# ==================== PAGE: VENTE (RAPIDE) ====================
def page_vente():
    mobile_header("Nouvelle Vente", "Scan ou sélection rapide")
    
    prod = pd.read_sql("SELECT * FROM produits WHERE stock>0", conn)
    
    if prod.empty:
        st.error("Aucun stock disponible")
        return
    
    # Recherche simple
    search = st.text_input("🔍 Rechercher un produit", placeholder="Nom ou code...")
    if search:
        prod = prod[prod["nom"].str.contains(search, case=False, na=False) | 
                   prod["code"].str.contains(search, case=False, na=False)]
    
    # Liste de produits sous forme de cartes cliquables
    st.markdown("### 📦 Produits disponibles")
    
    for _, row in prod.head(10).iterrows():
        with st.expander(f"{row['nom']} ({int(row['stock'])} disp.) - {mga(row['prix_vente'])}"):
            with st.form(f"vente_{row['id']}"):
                qte = st.number_input("Qté", 1, int(row["stock"]), 1, key=f"q_{row['id']}")
                pu = st.number_input("Prix", int(row["prix_vente"]), step=1000, key=f"p_{row['id']}")
                
                total = qte * pu
                st.markdown(f"**Total: {mga(total)}**")
                
                if st.form_submit_button("✅ Valider la vente"):
                    ref = f"V{datetime.now().strftime('%y%m%d%H%M')}"
                    conn.execute(
                        "INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers,ref) VALUES (?,?,?,?,?,?,?)",
                        (datetime.now().isoformat(), row["id"], 'VENTE', qte, pu, "Client direct", ref)
                    )
                    conn.execute("UPDATE produits SET stock=stock-? WHERE id=?", (qte, row["id"]))
                    conn.commit()
                    st.success("Vente enregistrée !")
                    st.balloons()

# ==================== PAGE: STOCK (ENTRÉE) ====================
def page_stock():
    mobile_header("Entrée Stock", "Réapprovisionnement rapide")
    
    prod = pd.read_sql("SELECT id, code, nom, stock FROM produits", conn)
    
    # Sélection rapide par recherche
    options = prod.apply(lambda x: f"{x['nom']} ({x['stock']})", axis=1).tolist()
    selected = st.selectbox("Produit", options=options)
    
    if selected:
        idx = options.index(selected)
        p = prod.iloc[idx]
        
        with st.form("entree_stock"):
            st.markdown(f"**Produit:** {p['nom']}")
            st.markdown(f"**Stock actuel:** {p['stock']}")
            
            qte = st.number_input("Quantité ajoutée", 1, step=1)
            pu = st.number_input("Prix d'achat unitaire", 0, step=1000)
            
            if st.form_submit_button("📥 Ajouter au stock"):
                conn.execute(
                    "INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers) VALUES (?,?,?,?,?,?)",
                    (datetime.now().isoformat(), p["id"], 'ACHAT', qte, pu, "Fournisseur")
                )
                conn.execute(
                    "UPDATE produits SET stock=stock+?, prix_achat=? WHERE id=?",
                    (qte, pu, p["id"])
                )
                conn.commit()
                st.success(f"+{qte} unités ajoutées !")
                st.rerun()

# ==================== PAGE: AJOUT PRODUIT ====================
def page_ajout():
    mobile_header("Nouveau Produit", "Création rapide")
    
    with st.form("add_prod_mobile"):
        cat = st.selectbox("Catégorie", ["TABLE", "CHAISE", "BUREAU", "ETAGERE", "AUTRE"])
        
        c1, c2 = st.columns(2)
        long = c1.number_input("Long", 0, step=5)
        larg = c2.number_input("Larg", 0, step=5)
        haut = st.number_input("Haut", 0, step=5)
        
        coul = st.selectbox("Couleur", LISTE_COULEURS)
        pieds = st.selectbox("Pieds", LISTE_PIEDS)
        
        st.divider()
        
        pa = st.number_input("Prix achat", 0, step=1000)
        pv = st.number_input("Prix vente", 0, step=1000)
        stock = st.number_input("Stock initial", 0)
        
        if st.form_submit_button("✅ Créer le produit"):
            nom_auto = f"{cat}.{long}.{larg}.{pieds}"
            c_clean = coul.replace("/", "").replace("#", "")
            p_clean = pieds.replace("/", "")
            code_auto = f"{cat}-{long}-{larg}-{haut}-{c_clean}-{p_clean}".upper().replace(" ", "")
            
            try:
                conn.execute(
                    """INSERT INTO produits (code,nom,categorie,hauteur,longueur,largeur,couleur,forme_pieds,prix_achat,prix_vente,stock) 
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (code_auto, nom_auto, cat, haut, long, larg, coul, pieds, pa, pv, stock)
                )
                conn.commit()
                st.success("Produit créé !")
                st.balloons()
            except:
                st.error("Erreur: Code existe déjà")

# ==================== PAGE: COMPTA SIMPLIFIÉE ====================
def page_compta():
    mobile_header("Comptabilité", "Flux du jour")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Ajout rapide dépense/recette
    with st.expander("➕ Ajouter une opération"):
        with st.form("add_op"):
            typ = st.segmented_control("Type", ["RECETTE", "DEPENSE"])
            des = st.text_input("Description")
            mnt = st.number_input("Montant", 0, step=1000)
            
            if st.form_submit_button("Enregistrer"):
                conn.execute(
                    "INSERT INTO journal(date,type,description,montant) VALUES (?,?,?,?)",
                    (today, typ, des, mnt)
                )
                conn.commit()
                st.success("Enregistré !")
    
    # Solde du jour
    rec = pd.read_sql(
        "SELECT SUM(montant) as val FROM journal WHERE type='RECETTE' AND date LIKE ?",
        conn, params=(today+"%",)
    ).val[0] or 0
    dep = pd.read_sql(
        "SELECT SUM(montant) as val FROM journal WHERE type='DEPENSE' AND date LIKE ?",
        conn, params=(today+"%",)
    ).val[0] or 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Entrées", mga(rec))
    c2.metric("Sorties", mga(dep))
    c3.metric("Solde", mga(rec-dep))
    
    # Historique du jour
    st.markdown("### 📜 Aujourd'hui")
    jour = pd.read_sql(
        "SELECT type, description, montant FROM journal WHERE date LIKE ? ORDER BY id DESC",
        conn, params=(today+"%",)
    )
    if not jour.empty:
        for _, row in jour.iterrows():
            color = "#10b981" if row["type"] == "RECETTE" else "#f43f5e"
            icon = "🟢" if row["type"] == "RECETTE" else "🔴"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center;
                 background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px;
                 margin-bottom: 8px; border-left: 3px solid {color};">
                <div>
                    <div style="color: {color}; font-weight: 600;">{icon} {row['description']}</div>
                </div>
                <div style="font-weight: 700; color: {color};">{mga(row['montant'])}</div>
            </div>
            """, unsafe_allow_html=True)

# ==================== ROUTING ====================
# Détection desktop vs mobile pour afficher sidebar ou non
def is_mobile():
    # Détection simple basée sur la largeur (via JS injecté)
    return st.session_state.get("is_mobile", True)

# Injecter JS pour détecter la taille d'écran
st.markdown("""
<script>
    const width = window.innerWidth;
    const isMobile = width < 768;
    // Stocker dans les query params ou cookies si nécessaire
    console.log("Mobile detected:", isMobile);
</script>
""", unsafe_allow_html=True)

# Affichage de la page courante
current_page = st.session_state.mobile_page

if current_page == "dashboard":
    page_dashboard()
elif current_page == "vente":
    page_vente()
elif current_page == "stock":
    page_stock()
elif current_page == "ajout":
    page_ajout()
elif current_page == "compta":
    page_compta()

# Affichage de la navigation mobile (toujours en dernier)
render_bottom_nav()

# Floating Action Button pour action principale selon la page
if current_page == "dashboard":
    if st.button("➕", key="fab"):
        st.session_state.mobile_page = "vente"
        st.rerun()
