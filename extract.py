import streamlit as st
import sqlite3, pandas as pd
from datetime import datetime, timedelta
import os

DB = "gestion_tables_mga.db"

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Melamine & Metallique",
    layout="wide",
    page_icon="🏗️",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONNALISÉ ---
st.markdown("""
<style>
/* ===== GLOBAL ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #e0e0e0 !important;
    font-size: 0.95rem;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    color: #00d4ff !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1);
}

/* ===== CARTES MÉTRIQUES ===== */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
    color: white;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.35);
}
div[data-testid="stMetric"] label {
    color: rgba(255,255,255,0.85) !important;
    font-weight: 500;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 700;
    font-size: 1.6rem !important;
}

/* Couleurs différentes pour chaque métrique */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    box-shadow: 0 8px 32px rgba(17, 153, 142, 0.25);
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #fc5c7d 0%, #6a82fb 100%);
    box-shadow: 0 8px 32px rgba(252, 92, 125, 0.25);
}

/* ===== HEADER ===== */
h1, h2 {
    background: linear-gradient(90deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
}

/* ===== DATAFRAMES ===== */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

/* ===== BOUTONS ===== */
.stButton > button {
    border-radius: 10px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
    border: none;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #667eea, #764ba2);
}

/* ===== FORM SUBMIT ===== */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    width: 100%;
    transition: all 0.3s ease;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
}

/* ===== EXPANDERS ===== */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
    border-radius: 12px !important;
    font-weight: 600;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #f0f2f6;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 8px 20px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
}

/* ===== INPUTS ===== */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 2px solid #e0e0e0 !important;
    transition: border-color 0.3s ease;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
}

/* ===== ALERTES ===== */
.stAlert {
    border-radius: 12px;
}

/* ===== CUSTOM CARDS ===== */
.custom-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.05);
    margin-bottom: 16px;
}
.stat-mini {
    text-align: center;
    padding: 12px;
    border-radius: 12px;
    background: #f8f9fa;
}
.stat-mini .number {
    font-size: 1.8rem;
    font-weight: 700;
    color: #667eea;
}
.stat-mini .label {
    font-size: 0.8rem;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Badge stock */
.stock-ok { 
    background: #d4edda; color: #155724; 
    padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;
}
.stock-low { 
    background: #fff3cd; color: #856404; 
    padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;
}
.stock-out { 
    background: #f8d7da; color: #721c24; 
    padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;
}

/* Logo sidebar */
.sidebar-logo {
    text-align: center;
    padding: 20px 10px;
}
.sidebar-logo h2 {
    background: linear-gradient(90deg, #00d4ff, #7b68ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.4rem;
    margin: 0;
}
.sidebar-logo p {
    color: rgba(255,255,255,0.5);
    font-size: 0.75rem;
    margin-top: 4px;
}

/* Page header */
.page-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0 20px 0;
    border-bottom: 3px solid;
    border-image: linear-gradient(90deg, #667eea, #764ba2) 1;
    margin-bottom: 24px;
}
.page-header .icon {
    font-size: 2.2rem;
}
.page-header .title {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.page-header .subtitle {
    color: #6c757d;
    font-size: 0.9rem;
    margin-top: 2px;
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

# --- LISTES DE CHOIX ---
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

MENU_ICONS = {
    "📊 Tableau de bord": "📊",
    "📦 Produits": "📦",
    "📥 Entrées Stock": "📥",
    "📤 Ventes": "📤",
    "📒 Journalier": "📒",
    "💰 Comptabilité": "💰",
}

# --- HELPER : En-tête de page ---
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

def stock_badge(val):
    if val <= 0:
        return f'<span class="stock-out">🔴 {val}</span>'
    elif val <= 3:
        return f'<span class="stock-low">🟡 {val}</span>'
    else:
        return f'<span class="stock-ok">🟢 {val}</span>'


# --- BARRE LATÉRALE ---
with st.sidebar:
    # Logo / Titre
    if os.path.exists("logo mm.jpg"):
        st.image("logo mm.jpg", use_container_width=True)
    else:
        st.markdown("""
        <div class="sidebar-logo">
            <h2>🏗️ Melamine & Metallique</h2>
            <p>Système de gestion</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    page = st.radio(
        "🧭 Navigation",
        list(MENU_ICONS.keys()),
        label_visibility="collapsed"
    )

    st.divider()

    # Mini stats sidebar
    prod_count = pd.read_sql("SELECT COUNT(*) as n FROM produits", conn).n[0]
    low_stock = pd.read_sql(
        "SELECT COUNT(*) as n FROM produits WHERE stock <= 3", conn
    ).n[0]

    st.markdown(f"""
    <div style="padding: 12px; background: rgba(255,255,255,0.05); 
         border-radius: 12px; margin-bottom: 12px;">
        <div style="color: rgba(255,255,255,0.6); font-size: 0.75rem; 
             text-transform: uppercase; letter-spacing: 1px;">
            Résumé rapide
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
            <div style="text-align:center;">
                <div style="color: #00d4ff; font-size: 1.4rem; font-weight: 700;">
                    {prod_count}
                </div>
                <div style="color: rgba(255,255,255,0.5); font-size: 0.7rem;">
                    Produits
                </div>
            </div>
            <div style="text-align:center;">
                <div style="color: #ff6b6b; font-size: 1.4rem; font-weight: 700;">
                    {low_stock}
                </div>
                <div style="color: rgba(255,255,255,0.5); font-size: 0.7rem;">
                    Stock bas
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("✨ By Lemur Tsena — v2.0")


# ============================================================
# --- TABLEAU DE BORD ---
# ============================================================
if page == "📊 Tableau de bord":
    page_header("📊", "Tableau de bord", 
                "Vue d'ensemble de votre activité")

    prod = pd.read_sql("SELECT * FROM produits", conn)
    valeur_stock = (prod["stock"] * prod["prix_vente"]).sum()

    mois_actuel = datetime.now().strftime("%Y-%m") + "%"
    v_prod = pd.read_sql(
        "SELECT SUM(qte*pu) as val FROM mouvements "
        "WHERE type='VENTE' AND date LIKE ?",
        conn, params=(mois_actuel,)
    ).val[0] or 0
    r_jour = pd.read_sql(
        "SELECT SUM(montant) as val FROM journal "
        "WHERE type='RECETTE' AND date LIKE ?",
        conn, params=(mois_actuel,)
    ).val[0] or 0
    total_recettes = v_prod + r_jour

    a_prod = pd.read_sql(
        "SELECT SUM(qte*pu) as val FROM mouvements "
        "WHERE type='ACHAT' AND date LIKE ?",
        conn, params=(mois_actuel,)
    ).val[0] or 0
    d_jour = pd.read_sql(
        "SELECT SUM(montant) as val FROM journal "
        "WHERE type='DEPENSE' AND date LIKE ?",
        conn, params=(mois_actuel,)
    ).val[0] or 0
    total_depenses = a_prod + d_jour

    benefice = total_recettes - total_depenses

    # KPI Cards
    c1, c2, c3 = st.columns(3)
    c1.metric("💎 Valeur du stock", mga(valeur_stock))
    c2.metric("📈 Recettes (Mois)", mga(total_recettes))
    c3.metric("🏆 Bénéfice Net (Mois)", mga(benefice))

    st.markdown("<br>", unsafe_allow_html=True)

    # Deux colonnes : Stock + Alertes
    col_left, col_right = st.columns([3, 1])

    with col_left:
        st.markdown("### 📦 État des stocks")

        if not prod.empty:
            # Filtre catégorie
            cats = ["Toutes"] + sorted(prod["categorie"].dropna().unique().tolist())
            filtre_cat = st.selectbox(
                "Filtrer par catégorie", cats, 
                label_visibility="collapsed"
            )
            if filtre_cat != "Toutes":
                prod_filtered = prod[prod["categorie"] == filtre_cat]
            else:
                prod_filtered = prod

            # Barre de recherche
            search = st.text_input(
                "🔍 Rechercher un produit...", 
                placeholder="Tapez un nom ou un code..."
            )
            if search:
                mask = (
                    prod_filtered["nom"].str.contains(search, case=False, na=False) |
                    prod_filtered["code"].str.contains(search, case=False, na=False)
                )
                prod_filtered = prod_filtered[mask]

            display_cols = [
                "code", "nom", "categorie", "stock", 
                "longueur", "largeur", "hauteur", "forme_pieds"
            ]
            st.dataframe(
                prod_filtered[display_cols].style.applymap(
                    lambda v: 'background-color: #ffe0e0' if isinstance(v, (int, float)) and v <= 0
                    else ('background-color: #fff3cd' if isinstance(v, (int, float)) and v <= 3 
                          else ''),
                    subset=['stock']
                ),
                use_container_width=True,
                height=400
            )
        else:
            st.info("Aucun produit enregistré. Ajoutez des produits dans la section 📦 Produits.")

    with col_right:
        st.markdown("### ⚠️ Alertes stock")

        low_items = prod[prod["stock"] <= 3].sort_values("stock")
        if not low_items.empty:
            for _, row in low_items.iterrows():
                if row["stock"] <= 0:
                    emoji, color = "🔴", "#f8d7da"
                else:
                    emoji, color = "🟡", "#fff3cd"
                st.markdown(f"""
                <div style="background: {color}; border-radius: 10px; 
                     padding: 10px 14px; margin-bottom: 8px; font-size: 0.85rem;">
                    {emoji} <strong>{row['nom']}</strong><br>
                    <span style="color: #666;">Stock: {int(row['stock'])}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #d4edda; border-radius: 10px; 
                 padding: 20px; text-align: center;">
                ✅<br><strong>Tous les stocks sont OK</strong>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# --- PRODUITS ---
# ============================================================
elif page == "📦 Produits":
    page_header("📦", "Catalogue des Produits", 
                "Gérez votre inventaire de meubles")

    df = pd.read_sql("SELECT * FROM produits", conn)

    # Onglets principaux
    tab_list, tab_add, tab_edit = st.tabs([
        "📋 Liste des produits", 
        "➕ Nouveau produit", 
        "✏️ Modifier / Supprimer"
    ])

    with tab_list:
        if not df.empty:
            # Filtres en ligne
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
                f_search = st.text_input(
                    "🔍 Recherche", 
                    placeholder="Nom, code...",
                    key="prod_fsearch"
                )

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

            df_display = df_view.drop(columns=["prix_achat", "id"])
            df_display["prix_vente"] = df_display["prix_vente"].apply(mga)

            # Stats rapides
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.markdown(f"""
            <div class="stat-mini">
                <div class="number">{len(df_view)}</div>
                <div class="label">Produits</div>
            </div>
            """, unsafe_allow_html=True)
            sc2.markdown(f"""
            <div class="stat-mini">
                <div class="number">{int(df_view['stock'].sum())}</div>
                <div class="label">Total stock</div>
            </div>
            """, unsafe_allow_html=True)
            sc3.markdown(f"""
            <div class="stat-mini">
                <div class="number" style="color:#11998e;">
                    {len(df_view[df_view['stock']>3])}
                </div>
                <div class="label">En stock</div>
            </div>
            """, unsafe_allow_html=True)
            sc4.markdown(f"""
            <div class="stat-mini">
                <div class="number" style="color:#e74c3c;">
                    {len(df_view[df_view['stock']<=0])}
                </div>
                <div class="label">Rupture</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(df_display, use_container_width=True, height=450)
        else:
            st.info("🛒 Aucun produit. Utilisez l'onglet ➕ pour en ajouter.")

    with tab_add:
        st.markdown("""
        <div class="custom-card">
            <strong>💡 Info :</strong> Le <em>nom</em> et le <em>code</em> 
            sont générés automatiquement à partir des caractéristiques.
        </div>
        """, unsafe_allow_html=True)

        with st.form("add_prod", clear_on_submit=True):
            st.markdown("#### 🏷️ Caractéristiques")
            c1, c2, c3 = st.columns(3)
            cat = c1.selectbox(
                "Catégorie", 
                ["TABLE", "CHAISE", "BUREAU", "ETAGERE", "AUTRE"]
            )
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
                    st.error(f"❌ Erreur : Ce code existe déjà ou données invalides.\n\n`{e}`")

    with tab_edit:
        if not df.empty:
            p_edit = st.selectbox(
                "Sélectionnez un produit",
                df.itertuples(),
                format_func=lambda x: f"🪑 {x.nom}  —  [{x.code}]  (Stock: {x.stock})"
            )

            st.markdown(f"""
            <div class="custom-card">
                <div style="display:flex; gap:30px; flex-wrap:wrap;">
                    <div><strong>📋 Nom :</strong> {p_edit.nom}</div>
                    <div><strong>🏷️ Code :</strong> <code>{p_edit.code}</code></div>
                    <div><strong>🎨 Couleur :</strong> {p_edit.couleur}</div>
                    <div><strong>📦 Stock :</strong> {p_edit.stock}</div>
                    <div><strong>💰 Prix vente :</strong> {mga(p_edit.prix_vente)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("edit_prod"):
                c1, c2 = st.columns(2)
                n_pv = c1.number_input(
                    "💲 Nouveau prix vente (Ar)", 
                    value=int(p_edit.prix_vente), step=1000
                )
                n_stock = c2.number_input(
                    "📦 Nouveau stock", 
                    value=int(p_edit.stock)
                )

                st.markdown("---")
                b1, b2 = st.columns(2)
                update = b1.form_submit_button(
                    "💾 Mettre à jour", use_container_width=True
                )
                delete = b2.form_submit_button(
                    "🗑️ Supprimer", use_container_width=True
                )

                if update:
                    conn.execute(
                        "UPDATE produits SET prix_vente=?, stock=? WHERE id=?",
                        (n_pv, n_stock, p_edit.id)
                    )
                    conn.commit()
                    st.success("✅ Produit mis à jour !")
                    st.rerun()
                if delete:
                    conn.execute(
                        "DELETE FROM produits WHERE id=?", (p_edit.id,)
                    )
                    conn.commit()
                    st.warning("🗑️ Produit supprimé.")
                    st.rerun()
        else:
            st.info("Aucun produit à modifier.")


# ============================================================
# --- ENTRÉES STOCK ---
# ============================================================
elif page == "📥 Entrées Stock":
    page_header("📥", "Entrée de Marchandise", 
                "Enregistrez vos achats et approvisionnements")

    prod = pd.read_sql("SELECT id, code, nom, stock FROM produits", conn)
    four = pd.read_sql("SELECT * FROM fournisseurs", conn)

    col_form, col_hist = st.columns([1, 1])

    with col_form:
        st.markdown("### 📝 Nouvelle entrée")
        with st.form("entree", clear_on_submit=True):
            p = st.selectbox(
                "📦 Produit",
                prod.itertuples(),
                format_func=lambda x: f"{x.nom}  [{x.code}]  (Stock: {x.stock})"
            )
            if not four.empty:
                f = st.selectbox(
                    "🏭 Fournisseur",
                    four.itertuples(),
                    format_func=lambda x: x.nom
                )
                f_nom = f.nom
            else:
                f_nom = st.text_input("🏭 Nom du fournisseur")

            c1, c2 = st.columns(2)
            qte = c1.number_input("📊 Quantité", 1, step=1)
            pu = c2.number_input("💲 Prix unitaire achat (Ar)", 0, step=1000)

            # Aperçu du total
            total = qte * pu
            st.markdown(f"""
            <div style="background: #e8f5e9; border-radius: 10px; 
                 padding: 14px; text-align: center; margin: 10px 0;">
                <span style="color: #2e7d32; font-weight: 600;">
                    Total : {mga(total)}
                </span>
            </div>
            """, unsafe_allow_html=True)

            submitted = st.form_submit_button(
                "✅ Valider l'achat", use_container_width=True
            )
            if submitted:
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
                st.success(f"✅ +{qte} unité(s) ajoutée(s) au stock de **{p.nom}**")
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
            st.dataframe(achats, use_container_width=True, height=400)
        else:
            st.info("Aucun achat enregistré.")


# ============================================================
# --- VENTES ---
# ============================================================
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
                    "📦 Produit",
                    prod.itertuples(),
                    format_func=lambda x: f"{x.nom}  (Stock: {x.stock})  —  {mga(x.prix_vente)}"
                )
                if not cli.empty:
                    c = st.selectbox(
                        "👤 Client",
                        cli.itertuples(),
                        format_func=lambda x: x.nom
                    )
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
                <div style="background: #e3f2fd; border-radius: 10px; 
                     padding: 14px; text-align: center;">
                    <div style="color: #666; font-size: 0.8rem;">TOTAL</div>
                    <div style="color: #1565c0; font-weight: 700; font-size: 1.2rem;">
                        {mga(total_vente)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                vc2.markdown(f"""
                <div style="background: {'#e8f5e9' if marge >= 0 else '#fbe9e7'}; 
                     border-radius: 10px; padding: 14px; text-align: center;">
                    <div style="color: #666; font-size: 0.8rem;">MARGE</div>
                    <div style="color: {'#2e7d32' if marge >= 0 else '#c62828'}; 
                         font-weight: 700; font-size: 1.2rem;">
                        {mga(marge)}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button(
                    "✅ Enregistrer la vente", use_container_width=True
                )
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
                st.dataframe(ventes, use_container_width=True, height=400)
            else:
                st.info("Aucune vente enregistrée.")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 4rem;">📦</div>
            <h3 style="color: #666;">Aucun stock disponible</h3>
            <p style="color: #999;">
                Tous vos produits sont en rupture. 
                Allez dans <strong>📥 Entrées Stock</strong> pour réapprovisionner.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# --- JOURNALIER ---
# ============================================================
elif page == "📒 Journalier":
    page_header("📒", "Journal des Opérations", 
                "Suivez vos dépenses et recettes quotidiennes")

    df_j = pd.read_sql(
        "SELECT id, date, type, description, montant "
        "FROM journal ORDER BY date DESC", conn
    )

    col1, col2 = st.columns([2, 3])

    with col1:
        t_add, t_edit = st.tabs(["➕ Ajouter", "✏️ Modifier / Suppr"])

        with t_add:
            with st.form("add_j", clear_on_submit=True):
                typ = st.selectbox(
                    "Type d'opération",
                    ["DEPENSE", "RECETTE"],
                    format_func=lambda x: f"{'🔴 Dépense' if x=='DEPENSE' else '🟢 Recette'}"
                )
                des = st.text_input("📝 Description")
                mnt = st.number_input("💲 Montant (Ar)", 0, step=1000)
                dat = st.date_input("📅 Date", datetime.now())

                # Preview
                if mnt > 0:
                    color = "#e8f5e9" if typ == "RECETTE" else "#fbe9e7"
                    icon = "🟢" if typ == "RECETTE" else "🔴"
                    st.markdown(f"""
                    <div style="background: {color}; border-radius: 10px; 
                         padding: 12px; text-align: center; margin: 8px 0;">
                        {icon} {mga(mnt)}
                    </div>
                    """, unsafe_allow_html=True)

                submitted = st.form_submit_button(
                    "✅ Enregistrer", use_container_width=True
                )
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
                        f"{'🔴' if x.type=='DEPENSE' else '🟢'} "
                        f"{x.date[:10]} | {x.description} | {mga(x.montant)}"
                    )
                )
                with st.form("edit_j"):
                    e_des = st.text_input("📝 Description", value=item.description)
                    e_mnt = st.number_input("💲 Montant", value=int(item.montant), step=1000)

                    st.markdown("---")
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 Mettre à jour", use_container_width=True):
                        conn.execute(
                            "UPDATE journal SET description=?, montant=? WHERE id=?",
                            (e_des, e_mnt, item.id)
                        )
                        conn.commit()
                        st.success("✅ Mis à jour !")
                        st.rerun()
                    if b2.form_submit_button("🗑️ Supprimer", use_container_width=True):
                        conn.execute("DELETE FROM journal WHERE id=?", (item.id,))
                        conn.commit()
                        st.warning("🗑️ Supprimé.")
                        st.rerun()
            else:
                st.info("Aucune opération enregistrée.")

    with col2:
        # KPI du journal
        today = datetime.now().strftime("%Y-%m-%d")
        rec_today = pd.read_sql(
            "SELECT SUM(montant) as val FROM journal "
            "WHERE type='RECETTE' AND date LIKE ?",
            conn, params=(today + "%",)
        ).val[0] or 0
        dep_today = pd.read_sql(
            "SELECT SUM(montant) as val FROM journal "
            "WHERE type='DEPENSE' AND date LIKE ?",
            conn, params=(today + "%",)
        ).val[0] or 0

        kc1, kc2, kc3 = st.columns(3)
        kc1.metric("🟢 Recettes aujourd'hui", mga(rec_today))
        kc2.metric("🔴 Dépenses aujourd'hui", mga(dep_today))
        kc3.metric("📊 Solde du jour", mga(rec_today - dep_today))

        st.markdown("<br>", unsafe_allow_html=True)

        # Tableau avec indicateurs visuels
        if not df_j.empty:
            df_display = df_j.drop(columns=["id"]).copy()
            df_display["montant"] = df_display["montant"].apply(mga)
            df_display["type"] = df_display["type"].apply(
                lambda x: "🟢 RECETTE" if x == "RECETTE" else "🔴 DÉPENSE"
            )
            st.dataframe(df_display, use_container_width=True, height=450)

            # Export CSV
            csv = df_j.drop(columns=["id"]).to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Exporter en CSV",
                csv,
                "journal.csv",
                "text/csv",
                use_container_width=True
            )


# ============================================================
# --- COMPTABILITÉ ---
# ============================================================
else:
    page_header("💰", "Comptabilité Générale", 
                "Synthèse financière complète")

    mouv = pd.read_sql(
        "SELECT type, (qte*pu) as montant FROM mouvements", conn
    )
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

    # Graphiques
    col_chart, col_detail = st.columns([2, 1])

    with col_chart:
        st.markdown("### 📈 Évolution financière")

        m_plot = pd.read_sql(
            "SELECT substr(date,1,10) as date, (qte*pu) as montant, type "
            "FROM mouvements", conn
        )
        j_plot = pd.read_sql(
            "SELECT substr(date,1,10) as date, montant, type FROM journal",
            conn
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

            # Graphique solde cumulé
            st.markdown("### 📊 Solde cumulé")
            chart_data['Solde'] = (chart_data['Recettes'] - chart_data['Dépenses']).cumsum()
            st.area_chart(chart_data[['Solde']])
        else:
            st.info("📊 Pas encore de données pour afficher les graphiques.")

    with col_detail:
        st.markdown("### 📋 Répartition")

        # Détail par catégorie
        ventes_detail = pd.read_sql(
            """SELECT p.categorie, SUM(m.qte*m.pu) as total 
               FROM mouvements m JOIN produits p ON m.produit_id=p.id
               WHERE m.type='VENTE' GROUP BY p.categorie
               ORDER BY total DESC""",
            conn
        )
        if not ventes_detail.empty:
            st.markdown("**🏷️ Ventes par catégorie**")
            for _, row in ventes_detail.iterrows():
                pct = (row['total'] / ventes_detail['total'].sum()) * 100
                st.markdown(f"""
                <div style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; 
                         font-size: 0.85rem; margin-bottom: 4px;">
                        <span>{row['categorie']}</span>
                        <span style="font-weight: 600;">{mga(row['total'])}</span>
                    </div>
                    <div style="background: #e0e0e0; border-radius: 10px; 
                         height: 8px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #667eea, #764ba2); 
                             width: {pct}%; height: 100%; border-radius: 10px;">
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Profit/Perte
        st.markdown(f"""
        <div style="background: {'#e8f5e9' if profit >= 0 else '#fbe9e7'}; 
             border-radius: 16px; padding: 24px; text-align: center;">
            <div style="font-size: 3rem;">
                {'🎉' if profit >= 0 else '⚠️'}
            </div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 8px;">
                {'Vous êtes en bénéfice !' if profit >= 0 else 'Attention, vous êtes en perte.'}
            </div>
            <div style="font-size: 1.6rem; font-weight: 700; 
                 color: {'#2e7d32' if profit >= 0 else '#c62828'}; margin-top: 8px;">
                {mga(profit)}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Bouton export
        all_mouv = pd.read_sql("SELECT * FROM mouvements", conn)
        all_jour = pd.read_sql("SELECT * FROM journal", conn)
        if not all_mouv.empty or not all_jour.empty:
            csv_m = all_mouv.to_csv(index=False).encode("utf-8")
            csv_j = all_jour.to_csv(index=False).encode("utf-8")
            ec1, ec2 = st.columns(2)
            ec1.download_button(
                "📥 Mouvements", csv_m, "mouvements.csv", 
                "text/csv", use_container_width=True
            )
            ec2.download_button(
                "📥 Journal", csv_j, "journal.csv", 
                "text/csv", use_container_width=True
            )
```

---

