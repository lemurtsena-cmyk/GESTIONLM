# Version Améliorée - Melamine & Metallique

Voici le code avec une interface significativement améliorée :

```python
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

DB = "gestion_tables_mga.db"

# ============================================================
# CONFIGURATION PAGE
# ============================================================
st.set_page_config(
    page_title="Melamine & Metallique",
    layout="wide",
    page_icon="🏗️",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS PERSONNALISÉ
# ============================================================
st.markdown("""
<style>
    /* Police et fond général */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fond principal */
    .main {
        background-color: #f0f2f6;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 8px 12px;
        margin: 3px 0;
        display: block;
        transition: background 0.3s;
        cursor: pointer;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.15);
    }

    /* Cards métriques personnalisées */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 5px solid #0f3460;
        margin-bottom: 16px;
    }
    .metric-card.green { border-left-color: #10b981; }
    .metric-card.red   { border-left-color: #ef4444; }
    .metric-card.blue  { border-left-color: #3b82f6; }
    .metric-card.gold  { border-left-color: #f59e0b; }

    .metric-label {
        font-size: 13px;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #1f2937;
        margin-top: 4px;
    }
    .metric-icon {
        font-size: 32px;
        float: right;
        margin-top: -8px;
    }

    /* Titres de page */
    .page-header {
        background: linear-gradient(135deg, #0f3460, #533483);
        color: white;
        padding: 20px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .page-header h1 {
        color: white !important;
        margin: 0;
        font-size: 24px;
        font-weight: 700;
    }
    .page-header p {
        color: rgba(255,255,255,0.75);
        margin: 4px 0 0 0;
        font-size: 14px;
    }

    /* Badges de stock */
    .badge-ok    { background:#d1fae5; color:#065f46; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-warn  { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-danger{ background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }

    /* Formulaires */
    .form-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 16px;
    }
    .form-title {
        font-size: 16px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Boutons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 8px 20px;
        transition: all 0.2s;
        border: none;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        font-weight: 600;
    }

    /* Séparateur sidebar */
    hr {
        border-color: rgba(255,255,255,0.15) !important;
    }

    /* Alertes */
    .stSuccess { border-radius: 10px; }
    .stWarning { border-radius: 10px; }
    .stError   { border-radius: 10px; }
    .stInfo    { border-radius: 10px; }

    /* Section titre */
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #374151;
        padding: 8px 0;
        border-bottom: 2px solid #e5e7eb;
        margin: 16px 0 12px 0;
    }

    /* Tag catégorie */
    .tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
    }
    .tag-table  { background:#dbeafe; color:#1e40af; }
    .tag-chaise { background:#f3e8ff; color:#6b21a8; }
    .tag-bureau { background:#dcfce7; color:#166534; }
    .tag-autre  { background:#fef9c3; color:#854d0e; }

</style>
""", unsafe_allow_html=True)


# ============================================================
# UTILS
# ============================================================
def mga(x):
    return f"{int(x or 0):,}".replace(",", " ") + " Ar"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def metric_card(label, value, icon, color="blue"):
    st.markdown(f"""
    <div class="metric-card {color}">
        <span class="metric-icon">{icon}</span>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def page_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div class="page-header">
        <span style="font-size:36px;">{icon}</span>
        <div>
            <h1>{title}</h1>
            {'<p>' + subtitle + '</p>' if subtitle else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def section_title(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

def stock_badge(qty):
    if qty > 10:
        return f'<span class="badge-ok">✅ {qty} en stock</span>'
    elif qty > 0:
        return f'<span class="badge-warn">⚠️ {qty} (faible)</span>'
    else:
        return f'<span class="badge-danger">❌ Rupture</span>'


# ============================================================
# INIT DB
# ============================================================
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

# ============================================================
# LISTES
# ============================================================
LISTE_PIEDS = ["/U", "/V", "/X", "/K", "/PLIABLE", "/TABOURET CARRE", "/TABOURET CERCLE"]
LISTE_COULEURS = [
    "/BLANC UNIS", "/NOIR UNIS", "/GRIS MARBRE", "#1023", "#1025", "#805",
    "#806", "#506", "#16854", "#16855", "#1010", "#8042", "#8052",
    "#932", "#809", "#308 BM", "#7058", "#76-1"
]
CATEGORIES = ["TABLE", "CHAISE", "BUREAU", "ETAGERE", "AUTRE"]


# ============================================================
# BARRE LATÉRALE
# ============================================================
with st.sidebar:
    st.markdown('<div style="text-align:center; padding: 10px 0;">', unsafe_allow_html=True)
    if os.path.exists("logo mm.jpg"):
        st.image("logo mm.jpg", use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:20px 0;">
            <span style="font-size:48px;">🏗️</span>
            <h2 style="color:white; margin:8px 0 4px 0; font-size:18px;">Melamine & Metallique</h2>
            <p style="color:rgba(255,255,255,0.5); font-size:12px; margin:0;">Gestion de stock</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    MENU_ITEMS = {
        "🏠  Tableau de bord": "Tableau de bord",
        "📦  Produits":        "Produits",
        "📥  Entrées Stock":   "Entrées Stock",
        "📤  Ventes":          "Ventes",
        "📒  Journalier":      "Journalier",
        "💰  Comptabilité":    "Comptabilité",
    }

    page_label = st.radio(
        "Navigation",
        list(MENU_ITEMS.keys()),
        label_visibility="collapsed"
    )
    page = MENU_ITEMS[page_label]

    st.divider()

    # Mini stats sidebar
    prod_count = pd.read_sql("SELECT COUNT(*) as n FROM produits", conn).n[0]
    rupture = pd.read_sql("SELECT COUNT(*) as n FROM produits WHERE stock=0", conn).n[0]
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.08); border-radius:12px; padding:14px; margin-bottom:12px;">
        <div style="font-size:12px; color:rgba(255,255,255,0.6); margin-bottom:8px; font-weight:600; text-transform:uppercase; letter-spacing:.05em;">Résumé rapide</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
            <span style="font-size:13px; color:rgba(255,255,255,0.8);">📦 Produits</span>
            <span style="font-weight:700; color:white;">{prod_count}</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="font-size:13px; color:rgba(255,255,255,0.8);">❌ Ruptures</span>
            <span style="font-weight:700; color:#f87171;">{rupture}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-top:20px;">
        <p style="color:rgba(255,255,255,0.3); font-size:11px;">Made with ❤️ by Lemur tsena</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE : TABLEAU DE BORD
# ============================================================
if page == "Tableau de bord":
    page_header("🏠", "Tableau de bord", "Vue d'ensemble de votre activité")

    prod = pd.read_sql("SELECT * FROM produits", conn)
    valeur_stock = (prod["stock"] * prod["prix_vente"]).sum()

    mois_actuel = datetime.now().strftime("%Y-%m") + "%"
    v_prod = pd.read_sql("SELECT SUM(qte*pu) as val FROM mouvements WHERE type='VENTE' AND date LIKE ?",
                         conn, params=(mois_actuel,)).val[0] or 0
    r_jour = pd.read_sql("SELECT SUM(montant) as val FROM journal WHERE type='RECETTE' AND date LIKE ?",
                         conn, params=(mois_actuel,)).val[0] or 0
    total_recettes = v_prod + r_jour

    a_prod = pd.read_sql("SELECT SUM(qte*pu) as val FROM mouvements WHERE type='ACHAT' AND date LIKE ?",
                         conn, params=(mois_actuel,)).val[0] or 0
    d_jour = pd.read_sql("SELECT SUM(montant) as val FROM journal WHERE type='DEPENSE' AND date LIKE ?",
                         conn, params=(mois_actuel,)).val[0] or 0
    total_depenses = a_prod + d_jour
    benefice = total_recettes - total_depenses

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Valeur du Stock", mga(valeur_stock), "🏗️", "blue")
    with c2:
        metric_card("Recettes (Mois)", mga(total_recettes), "📈", "green")
    with c3:
        metric_card("Dépenses (Mois)", mga(total_depenses), "📉", "red")
    with c4:
        color = "green" if benefice >= 0 else "red"
        metric_card("Bénéfice Net", mga(benefice), "💰", color)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 1])

    with col_a:
        section_title("📦 État des Stocks")
        if not prod.empty:
            display = prod[["code", "nom", "categorie", "stock", "longueur",
                            "largeur", "hauteur", "forme_pieds", "prix_vente"]].copy()
            display["prix_vente"] = display["prix_vente"].apply(mga)
            display.columns = ["Code", "Nom", "Catégorie", "Stock", "Long.", "Larg.", "Haut.", "Pieds", "Prix Vente"]
            st.dataframe(display, use_container_width=True, height=320)
        else:
            st.info("Aucun produit enregistré.")

    with col_b:
        section_title("🚨 Alertes Stock")
        faible = prod[prod["stock"] <= 5]
        if faible.empty:
            st.success("✅ Tous les stocks sont suffisants !")
        else:
            for _, r in faible.iterrows():
                color = "#fee2e2" if r.stock == 0 else "#fef3c7"
                icon = "❌" if r.stock == 0 else "⚠️"
                st.markdown(f"""
                <div style="background:{color}; border-radius:10px; padding:10px 14px; margin-bottom:8px;">
                    <strong>{icon} {r['nom']}</strong><br>
                    <span style="font-size:13px; color:#555;">Stock : <b>{int(r['stock'])}</b></span>
                </div>
                """, unsafe_allow_html=True)

        section_title("🏷️ Par Catégorie")
        if not prod.empty:
            cat_stats = prod.groupby("categorie")["stock"].sum().reset_index()
            cat_stats.columns = ["Catégorie", "Stock total"]
            st.dataframe(cat_stats, use_container_width=True, hide_index=True)


# ============================================================
# PAGE : PRODUITS
# ============================================================
elif page == "Produits":
    page_header("📦", "Catalogue des Produits", "Gérez votre catalogue de produits")

    df = pd.read_sql("SELECT * FROM produits", conn)

    # Barre de recherche + filtre
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search = st.text_input("🔍 Rechercher un produit...", placeholder="Nom, code, catégorie...")
    with col_filter:
        cat_filter = st.selectbox("Filtrer catégorie", ["Toutes"] + CATEGORIES)

    # Filtrage
    df_view = df.copy()
    if search:
        mask = (df_view["nom"].str.contains(search, case=False, na=False) |
                df_view["code"].str.contains(search, case=False, na=False) |
                df_view["categorie"].str.contains(search, case=False, na=False))
        df_view = df_view[mask]
    if cat_filter != "Toutes":
        df_view = df_view[df_view["categorie"] == cat_filter]

    # Affichage tableau
    if not df_view.empty:
        display = df_view.drop(columns=["prix_achat", "id"]).copy()
        display["prix_vente"] = display["prix_vente"].apply(mga)
        display.columns = ["Code", "Nom", "Catégorie", "Hauteur", "Longueur",
                           "Largeur", "Couleur", "Pieds", "Prix Vente", "Stock"]
        st.dataframe(display, use_container_width=True, height=280)
        st.caption(f"📋 {len(df_view)} produit(s) affiché(s)")
    else:
        st.info("Aucun produit trouvé.")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # ---- AJOUTER ----
    with col1:
        with st.expander("➕ Ajouter un nouveau produit", expanded=False):
            st.markdown('<div class="form-title">🆕 Informations du produit</div>', unsafe_allow_html=True)
            st.info("ℹ️ Le **NOM** et le **CODE** sont générés automatiquement.")
            with st.form("add_prod"):
                c1, c2, c3 = st.columns(3)
                cat  = c1.selectbox("Catégorie", CATEGORIES)
                coul = c2.selectbox("Couleur", LISTE_COULEURS)
                pieds = c3.selectbox("Forme des pieds", LISTE_PIEDS)

                st.markdown("**📐 Dimensions**")
                c1, c2, c3 = st.columns(3)
                long = c1.number_input("Longueur (cm)", 0, step=5)
                larg = c2.number_input("Largeur (cm)", 0, step=5)
                haut = c3.number_input("Hauteur (cm)", 0, step=5)

                st.markdown("**💵 Tarification**")
                c1, c2 = st.columns(2)
                pa = c1.number_input("Prix d'achat (Ar)", 0, step=1000)
                pv = c2.number_input("Prix de vente (Ar)", 0, step=1000)
                stock = st.number_input("Stock initial", 0, step=1)

                submitted = st.form_submit_button("✅ Enregistrer le produit",
                                                  use_container_width=True)
                if submitted:
                    nom_auto  = f"{cat}.{long}.{larg}.{pieds}"
                    c_clean   = coul.replace("/", "").replace("#", "")
                    p_clean   = pieds.replace("/", "")
                    code_auto = f"{cat}-{long}-{larg}-{haut}-{c_clean}-{p_clean}".upper().replace(" ", "")
                    try:
                        conn.execute("""INSERT INTO produits
                            (code, nom, categorie, hauteur, longueur, largeur,
                             couleur, forme_pieds, prix_achat, prix_vente, stock)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                            (code_auto, nom_auto, cat, haut, long, larg,
                             coul, pieds, pa, pv, stock))
                        conn.commit()
                        st.success(f"✅ Produit créé : **{nom_auto}**")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur : Code déjà existant ou données invalides.\n{e}")

    # ---- MODIFIER / SUPPRIMER ----
    with col2:
        with st.expander("✏️ Modifier / Supprimer un produit", expanded=False):
            if not df.empty:
                p_edit = st.selectbox(
                    "Sélectionner un produit",
                    list(df.itertuples()),
                    format_func=lambda x: f"{x.nom}  |  {x.code}"
                )
                st.markdown(f"""
                <div style="background:#f0f9ff; border-radius:10px; padding:12px 16px; margin:10px 0;">
                    <b>📋 Produit sélectionné :</b> {p_edit.nom}<br>
                    <small style="color:#555;">Code : {p_edit.code} | Stock actuel : {p_edit.stock}</small>
                </div>
                """, unsafe_allow_html=True)
                with st.form("edit_prod"):
                    n_pv    = st.number_input("💵 Prix de vente (Ar)", value=int(p_edit.prix_vente), step=1000)
                    n_pa    = st.number_input("🛒 Prix d'achat (Ar)",  value=int(p_edit.prix_achat),  step=1000)
                    n_stock = st.number_input("📦 Stock",               value=int(p_edit.stock),        step=1)

                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 Mettre à jour", use_container_width=True):
                        conn.execute("UPDATE produits SET prix_vente=?, prix_achat=?, stock=? WHERE id=?",
                                     (n_pv, n_pa, n_stock, p_edit.id))
                        conn.commit()
                        st.success("✅ Produit mis à jour !")
                        st.rerun()
                    if b2.form_submit_button("🗑️ Supprimer", use_container_width=True):
                        conn.execute("DELETE FROM produits WHERE id=?", (p_edit.id,))
                        conn.commit()
                        st.warning("🗑️ Produit supprimé.")
                        st.rerun()
            else:
                st.info("Aucun produit disponible.")


# ============================================================
# PAGE : ENTRÉES STOCK
# ============================================================
elif page == "Entrées Stock":
    page_header("📥", "Entrée de Marchandise", "Enregistrer les achats fournisseurs")

    prod = pd.read_sql("SELECT id, code, nom, stock FROM produits", conn)
    four = pd.read_sql("SELECT * FROM fournisseurs", conn)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        section_title("📋 Nouveau bon d'entrée")
        with st.form("entree"):
            if prod.empty:
                st.warning("⚠️ Aucun produit en catalogue.")
            else:
                p = st.selectbox("📦 Produit",
                                 list(prod.itertuples()),
                                 format_func=lambda x: f"{x.nom} ({x.code}) — Stock: {x.stock}")
            if four.empty:
                st.warning("⚠️ Aucun fournisseur enregistré.")
                f_nom = st.text_input("Nom du fournisseur (manuel)")
            else:
                f = st.selectbox("🏭 Fournisseur",
                                 list(four.itertuples()),
                                 format_func=lambda x: x.nom)
                f_nom = f.nom

            c1, c2 = st.columns(2)
            qte = c1.number_input("📊 Quantité", 1, step=1)
            pu  = c2.number_input("💵 Prix unitaire (Ar)", 0, step=500)

            total_achat = qte * pu
            st.markdown(f"""
            <div style="background:#f0fdf4; border-radius:10px; padding:12px; text-align:center; margin:8px 0;">
                <span style="font-size:13px; color:#555;">Total achat estimé</span><br>
                <span style="font-size:22px; font-weight:700; color:#059669;">{mga(total_achat)}</span>
            </div>
            """, unsafe_allow_html=True)

            if st.form_submit_button("✅ Valider l'entrée", use_container_width=True):
                if not prod.empty:
                    conn.execute(
                        "INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers) VALUES (?,?,?,?,?,?)",
                        (datetime.now().isoformat(), p.id, 'ACHAT', qte, pu, f_nom))
                    conn.execute("UPDATE produits SET stock=stock+?, prix_achat=? WHERE id=?",
                                 (qte, pu, p.id))
                    conn.commit()
                    st.success(f"✅ {qte} unité(s) ajoutée(s) au stock !")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        section_title("📜 Historique des entrées")
        hist = pd.read_sql("""
            SELECT m.date, p.nom, m.qte, m.pu, (m.qte*m.pu) as total, m.tiers
            FROM mouvements m
            JOIN produits p ON m.produit_id = p.id
            WHERE m.type='ACHAT'
            ORDER BY m.date DESC LIMIT 30
        """, conn)
        if not hist.empty:
            hist["pu"]    = hist["pu"].apply(mga)
            hist["total"] = hist["total"].apply(mga)
            hist["date"]  = pd.to_datetime(hist["date"]).dt.strftime("%d/%m/%Y %H:%M")
            hist.columns  = ["Date", "Produit", "Qté", "P.U.", "Total", "Fournisseur"]
            st.dataframe(hist, use_container_width=True, height=400)
        else:
            st.info("Aucune entrée enregistrée.")

        section_title("🏭 Gérer les fournisseurs")
        with st.expander("➕ Ajouter un fournisseur"):
            with st.form("add_four"):
                nom_f = st.text_input("Nom du fournisseur")
                tel_f = st.text_input("Téléphone")
                if st.form_submit_button("Enregistrer", use_container_width=True):
                    conn.execute("INSERT INTO fournisseurs(nom,tel) VALUES (?,?)", (nom_f, tel_f))
                    conn.commit()
                    st.success("✅ Fournisseur ajouté !")
                    st.rerun()


# ============================================================
# PAGE : VENTES
# ============================================================
elif page == "Ventes":
    page_header("📤", "Vente / Facturation", "Enregistrer les ventes et générer des références")

    prod = pd.read_sql("SELECT * FROM produits WHERE stock>0", conn)
    cli  = pd.read_sql("SELECT * FROM clients", conn)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        section_title("🛒 Nouvelle vente")
        if prod.empty:
            st.warning("⚠️ Aucun produit en stock disponible.")
        else:
            with st.form("vente"):
                p = st.selectbox("📦 Produit",
                                 list(prod.itertuples()),
                                 format_func=lambda x: f"{x.nom}  (Stock: {x.stock})")

                # Aperçu produit
                st.markdown(f"""
                <div style="background:#eff6ff; border-radius:10px; padding:10px 14px; margin:8px 0;">
                    🏷️ <b>Prix catalogue :</b> {mga(p.prix_vente)} &nbsp;|&nbsp;
                    📐 {p.longueur}×{p.largeur}×{p.hauteur} cm &nbsp;|&nbsp;
                    🎨 {p.couleur}
                </div>
                """, unsafe_allow_html=True)

                if cli.empty:
                    c_nom = st.text_input("Nom du client (manuel)")
                else:
                    c = st.selectbox("👤 Client",
                                     list(cli.itertuples()),
                                     format_func=lambda x: x.nom)
                    c_nom = c.nom

                c1, c2 = st.columns(2)
                qte = c1.number_input("📊 Quantité", 1, max_value=int(p.stock), step=1)
                pu  = c2.number_input("💵 Prix vente (Ar)", int(p.prix_vente), step=500)

                marge = pu - p.prix_achat
                total = qte * pu
                col_t1, col_t2 = st.columns(2)
                col_t1.markdown(f"""
                <div style="background:#f0fdf4; border-radius:10px; padding:12px; text-align:center;">
                    <div style="font-size:12px; color:#555;">Total vente</div>
                    <div style="font-size:20px; font-weight:700; color:#059669;">{mga(total)}</div>
                </div>
                """, unsafe_allow_html=True)
                col_t2.markdown(f"""
                <div style="background:#eff6ff; border-radius:10px; padding:12px; text-align:center;">
                    <div style="font-size:12px; color:#555;">Marge unitaire</div>
                    <div style="font-size:20px; font-weight:700; color:#2563eb;">{mga(marge)}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("✅ Enregistrer la vente", use_container_width=True):
                    ref = f"V{datetime.now().strftime('%y%m%d%H%M%S')}"
                    conn.execute(
                        "INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers,ref) VALUES (?,?,?,?,?,?,?)",
                        (datetime.now().isoformat(), p.id, 'VENTE', qte, pu, c_nom, ref))
                    conn.execute("UPDATE produits SET stock=stock-? WHERE id=?", (qte, p.id))
                    conn.commit()
                    st.success(f"🎉 Vente enregistrée ! Réf. : **{ref}**")
                    st.balloons()
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        section_title("📜 Historique des ventes")
        hist_v = pd.read_sql("""
            SELECT m.date, m.ref, p.nom, m.qte, m.pu, (m.qte*m.pu) as total, m.tiers
            FROM mouvements m
            JOIN produits p ON m.produit_id = p.id
            WHERE m.type='VENTE'
            ORDER BY m.date DESC LIMIT 30
        """, conn)
        if not hist_v.empty:
            hist_v["pu"]    = hist_v["pu"].apply(mga)
            hist_v["total"] = hist_v["total"].apply(mga)
            hist_v["date"]  = pd.to_datetime(hist_v["date"]).dt.strftime("%d/%m/%Y %H:%M")
            hist_v.columns  = ["Date", "Réf.", "Produit", "Qté", "P.U.", "Total", "Client"]
            st.dataframe(hist_v, use_container_width=True, height=360)
        else:
            st.info("Aucune vente enregistrée.")

        section_title("👥 Gérer les clients")
        with st.expander("➕ Ajouter un client"):
            with st.form("add_cli"):
                nom_c = st.text_input("Nom du client")
                tel_c = st.text_input("Téléphone")
                if st.form_submit_button("Enregistrer", use_container_width=True):
                    conn.execute("INSERT INTO clients(nom,tel) VALUES (?,?)", (nom_c, tel_c))
                    conn.commit()
                    st.success("✅ Client ajouté !")
                    st.rerun()


# ============================================================
# PAGE : JOURNALIER
# ============================================================
elif page == "Journalier":
    page_header("📒", "Journal Journalier", "Recettes et dépenses hors stock")

    df_j = pd.read_sql(
        "SELECT id, date, type, description, montant FROM journal ORDER BY date DESC", conn)

    col1, col2 = st.columns([1, 2])

    with col1:
        t_add, t_edit = st.tabs(["➕ Ajouter", "✏️ Modifier"])

        with t_add:
            with st.form("add_j"):
                typ = st.selectbox("📋 Type", ["DEPENSE", "RECETTE"],
                                   format_func=lambda x: f"{'💸' if x=='DEPENSE' else '💰'} {x}")
                des = st.text_input("📝 Description")
                mnt = st.number_input("💵 Montant (Ar)", 0, step=500)
                dat = st.date_input("📅 Date", datetime.now())
                if st.form_submit_button("✅ Enregistrer", use_container_width=True):
                    conn.execute(
                        "INSERT INTO journal(date,type,description,montant) VALUES (?,?,?,?)",
                        (dat.isoformat(), typ, des, mnt))
                    conn.commit()
                    st.success("✅ Opération enregistrée !")
                    st.rerun()

        with t_edit:
            if not df_j.empty:
                item = st.selectbox(
                    "Sélectionner",
                    list(df_j.itertuples()),
                    format_func=lambda x: f"{x.date[:10]} | {x.description[:25]}")
                with st.form("edit_j"):
                    e_des = st.text_input("Description", value=item.description)
                    e_mnt = st.number_input("Montant", value=int(item.montant), step=500)
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 MAJ", use_container_width=True):
                        conn.execute(
                            "UPDATE journal SET description=?, montant=? WHERE id=?",
                            (e_des, e_mnt, item.id))
                        conn.commit()
                        st.success("✅ Mis à jour !")
                        st.rerun()
                    if b2.form_submit_button("🗑️ Suppr.", use_container_width=True):
                        conn.execute("DELETE FROM journal WHERE id=?", (item.id,))
                        conn.commit()
                        st.warning("🗑️ Supprimé.")
                        st.rerun()
            else:
                st.info("Aucune opération.")

    with col2:
        section_title("📊 Récapitulatif du jour")
        today = datetime.now().strftime("%Y-%m-%d")
        rec_j  = df_j[(df_j.type == "RECETTE") & (df_j.date.str.startswith(today))]["montant"].sum()
        dep_j  = df_j[(df_j.type == "DEPENSE") & (df_j.date.str.startswith(today))]["montant"].sum()

        cc1, cc2 = st.columns(2)
        with cc1:
            metric_card("Recettes aujourd'hui", mga(rec_j), "💰", "green")
        with cc2:
            metric_card("Dépenses aujourd'hui", mga(dep_j), "💸", "red")

        section_title("📋 Toutes les opérations")
        if not df_j.empty:
            display_j = df_j.copy()
            display_j["montant"] = display_j["montant"].apply(mga)
            display_j["date"]    = pd.to_datetime(display_j["date"]).dt.strftime("%d/%m/%Y")
            display_j = display_j.drop(columns=["id"])
            display_j.columns = ["Date", "Type", "Description", "Montant"]
            st.dataframe(display_j, use_container_width=True, height=380)
        else:
            st.info("Aucune opération enregistrée.")


# ============================================================
# PAGE : COMPTABILITÉ
# ============================================================
else:
    page_header("💰", "Comptabilité", "Bilan financier global de l'entreprise")

    mouv = pd.read_sql("SELECT type, (qte*pu) as montant FROM mouvements", conn)
    jour = pd.read_sql("SELECT type, montant FROM journal", conn)

    recettes  = (mouv[mouv.type == 'VENTE']['montant'].sum()
                 + jour[jour.type == 'RECETTE']['montant'].sum())
    depenses  = (mouv[mouv.type == 'ACHAT']['montant'].sum()
                 + jour[jour.type == 'DEPENSE']['montant'].sum())
    benefice  = recettes - depenses
    taux_marge = (benefice / recettes * 100) if recettes > 0 else 0

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Recettes", mga(recettes), "📈", "green")
    with c2:
        metric_card("Total Dépenses", mga(depenses), "📉", "red")
    with c3:
        metric_card("Profit Global", mga(benefice), "💰", "green" if benefice >= 0 else "red")
    with c4:
        metric_card("Taux de Marge", f"{taux_marge:.1f} %", "📊", "blue")

    st.markdown("<br>", unsafe_allow_html=True)

    col_g, col_d = st.columns([2, 1])

    with col_g:
        section_title("📈 Évolution Recettes / Dépenses")
        m_plot = pd.read_sql(
            "SELECT substr(date,1,10) as date, (qte*pu) as montant, type FROM mouvements", conn)
        j_plot = pd.read_sql(
            "SELECT substr(date,1,10) as date, montant, type FROM journal", conn)
        total_data = pd.concat([m_plot, j_plot])

        if not total_data.empty:
            total_data["Recettes"] = total_data.apply(
                lambda x: x["montant"] if x["type"] in ["VENTE", "RECETTE"] else 0, axis=1)
            total_data["Dépenses"] = total_data.apply(
                lambda x: x["montant"] if x["type"] in ["ACHAT", "DEPENSE"] else 0, axis=1)
            chart_data = total_data.groupby("date")[["Recettes", "Dépenses"]].sum()
            st.line_chart(chart_data, color=["#10b981", "#ef4444"])
        else:
            st.info("Pas encore de données pour le graphique.")

    with col_d:
        section_title("🏆 Top Ventes")
        top = pd.read_sql("""
            SELECT p.nom, SUM(m.qte) as qte, SUM(m.qte*m.pu) as ca
            FROM mouvements m
            JOIN produits p ON m.produit_id = p.id
            WHERE m.type='VENTE'
            GROUP BY p.nom
            ORDER BY ca DESC LIMIT 8
        """, conn)
        if not top.empty:
            top["ca"] = top["ca"].apply(mga)
            top.columns = ["Produit", "Qté vendues", "CA"]
            st.dataframe(top, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune vente enregistrée.")

        section_title("📊 Répartition par type")
        r1, r2 = st.columns(2)
        v_total = mouv[mouv.type == 'VENTE']['montant'].sum()
        a_total = mouv[mouv.type == 'ACHAT']['montant'].sum()
        r1.markdown(f"""
        <div style="background:#f0fdf4; border-radius:10px; padding:12px; text-align:center;">
            <div style="font-size:12px; color:#555;">CA Ventes</div>
            <div style="font-weight:700; color:#059669;">{mga(v_total)}</div>
        </div>
        """, unsafe_allow_html=True)
        r2.markdown(f"""
        <div style="background:#fef2f2; border-radius:10px; padding:12px; text-align:center;">
            <div style="font-size:12px; color:#555;">CA Achats</div>
            <div style="font-weight:700; color:#dc2626;">{mga(a_total)}</div>
        </div>
        """, unsafe_allow_html=True)
```

---

## 🎨 Améliorations apportées

| Domaine | Amélioration |
|---|---|
| **Sidebar** | Fond dégradé sombre, mini-stats (produits / ruptures), navigation stylée |
| **En-têtes de pages** | Bannières colorées avec icône + sous-titre |
| **KPI Cards** | Cartes avec bordure colorée, icônes, typographie améliorée |
| **Alertes Stock** | Panneau dédié avec badges rouge/orange/vert |
| **Tableaux** | Colonnes renommées en français, hauteur fixe, coins arrondis |
| **Formulaires** | Aperçu du total en temps réel, sections séparées |
| **Historique** | Ajout des historiques Achats et Ventes dans les pages dédiées |
| **Comptabilité** | Graphique double courbe (recettes vs dépenses), Top 8 ventes |
| **Fournisseurs/Clients** | Gestion directement depuis les pages Entrées/Ventes |
