import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Furniture Manager MGA", layout="wide", page_icon="📈")

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

DB = "mga_business_pro.db"

# --- FONCTIONS TECHNIQUES ---
def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def mga(x):
    return f"{int(x or 0):,}".replace(",", " ") + " Ar"

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE, nom TEXT, categorie TEXT,
            prix_achat REAL, prix_vente REAL, qte INTEGER, qte_min INTEGER
        );
        CREATE TABLE IF NOT EXISTS flux (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, type TEXT, produit_id INTEGER, 
            qte INTEGER, pu REAL, tiers TEXT, ref TEXT
        );
    """)
    conn.commit()

init_db()

# --- NAVIGATION ---
with st.sidebar:
    st.title("🛋️ MGA Mobiliers")
    menu = st.radio("Navigation", ["Tableau de Bord", "Gestion Stock", "Nouvelle Transaction", "Historique & Rapports"])
    st.divider()
    st.info("Système de gestion de stock v2.0")

# --- 1. TABLEAU DE BORD ---
if menu == "Tableau de Bord":
    st.header("📊 Vue d'ensemble")
    
    conn = get_conn()
    df_stock = pd.read_sql("SELECT * FROM stock", conn)
    df_flux = pd.read_sql("SELECT * FROM flux", conn)
    
    # KPIs
    valeur_stock = (df_stock['qte'] * df_stock['prix_achat']).sum()
    ventes_totales = df_flux[df_flux['type'] == 'VENTE']['qte'].sum()
    ca = (df_flux[df_flux['type'] == 'VENTE']['qte'] * df_flux[df_flux['type'] == 'VENTE']['pu']).sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Valeur Stock", mga(valeur_stock))
    col2.metric("Chiffre d'Affaires", mga(ca))
    col3.metric("Articles vendus", int(ventes_totales))
    col4.metric("Produits en catalogue", len(df_stock))

    # Graphiques
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("📦 État des Stocks")
        fig_stock = px.bar(df_stock, x='nom', y='qte', color='qte', 
                           title="Quantité par produit", color_continuous_scale="Viridis")
        st.plotly_chart(fig_stock, use_container_width=True)
        
    with c2:
        st.subheader("⚠️ Alertes Réapprovisionnement")
        alertes = df_stock[df_stock['qte'] <= df_stock['qte_min']]
        if not alertes.empty:
            st.error(f"{len(alertes)} produits sont en stock critique !")
            st.table(alertes[['nom', 'qte', 'qte_min']])
        else:
            st.success("Tous les stocks sont suffisants.")

# --- 2. GESTION STOCK ---
elif menu == "Gestion Stock":
    st.header("🗃️ Gestion du Catalogue")
    
    tab1, tab2 = st.tabs(["Liste des produits", "Ajouter un produit"])
    
    with tab1:
        conn = get_conn()
        df = pd.read_sql("SELECT * FROM stock", conn)
        
        # Recherche
        search = st.text_input("🔍 Rechercher un produit (Nom ou Code)")
        if search:
            df = df[df['nom'].str.contains(search, case=False) | df['code'].str.contains(search, case=False)]
            
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    with tab2:
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            code = c1.text_input("Code Unique")
            nom = c2.text_input("Nom de l'article")
            cat = st.selectbox("Catégorie", ["Tables", "Chaises", "Bureaux", "Armoires", "Autres"])
            c3, c4, c5 = st.columns(3)
            pa = c3.number_input("Prix d'Achat (Ar)", min_value=0)
            pv = c4.number_input("Prix de Vente (Ar)", min_value=0)
            qte_i = c5.number_input("Stock Initial", min_value=0)
            
            if st.form_submit_button("Enregistrer le produit"):
                try:
                    conn = get_conn()
                    conn.execute("INSERT INTO stock (code, nom, categorie, prix_achat, prix_vente, qte, qte_min) VALUES (?,?,?,?,?,?,?)",
                                 (code, nom, cat, pa, pv, qte_i, 2))
                    conn.commit()
                    st.success("Produit ajouté avec succès !")
                    st.rerun()
                except:
                    st.error("Erreur : Le code produit existe déjà.")

# --- 3. TRANSACTION ---
elif menu == "Nouvelle Transaction":
    st.header("🔄 Entrée / Sortie de Stock")
    
    conn = get_conn()
    produits = pd.read_sql("SELECT id, nom, code, qte, prix_vente, prix_achat FROM stock", conn)
    
    type_t = st.radio("Type de mouvement", ["VENTE (Sortie)", "ACHAT (Entrée Fournisseur)"], horizontal=True)
    
    with st.container(border=True):
        prod_sel = st.selectbox("Sélectionner le produit", produits.itertuples(), format_func=lambda x: f"{x.code} - {x.nom} (Dispo: {x.qte})")
        
        c1, c2 = st.columns(2)
        qte = c1.number_input("Quantité", min_value=1)
        tiers = c2.text_input("Client / Fournisseur")
        
        # Prix par défaut selon transaction
        prix_defaut = prod_sel.prix_vente if "VENTE" in type_t else prod_sel.prix_achat
        pu = st.number_input("Prix Unitaire (Ar)", value=float(prix_defaut))
        
        if st.button("Valider la transaction", use_container_width=True):
            type_db = "VENTE" if "VENTE" in type_t else "ACHAT"
            
            # Vérification stock pour vente
            if type_db == "VENTE" and qte > prod_sel.qte:
                st.error("Stock insuffisant !")
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute("INSERT INTO flux (date, type, produit_id, qte, pu, tiers) VALUES (?,?,?,?,?,?)",
                             (now, type_db, prod_sel.id, qte, pu, tiers))
                
                # Update stock
                modif = -qte if type_db == "VENTE" else qte
                conn.execute("UPDATE stock SET qte = qte + ? WHERE id = ?", (modif, prod_sel.id))
                conn.commit()
                st.success("Transaction enregistrée !")
                st.balloons()

# --- 4. RAPPORTS ---
elif menu == "Historique & Rapports":
    st.header("📜 Historique des mouvements")
    
    conn = get_conn()
    query = """
        SELECT f.date, f.type, s.nom as produit, f.qte, f.pu, (f.qte * f.pu) as total, f.tiers 
        FROM flux f 
        JOIN stock s ON f.produit_id = s.id
        ORDER BY f.id DESC
    """
    df_hist = pd.read_sql(query, conn)
    
    # Filtres
    f_type = st.multiselect("Filtrer par type", ["VENTE", "ACHAT"], default=["VENTE", "ACHAT"])
    df_filtered = df_hist[df_hist['type'].isin(f_type)]
    
    st.dataframe(df_filtered, use_container_width=True)
    
    # Export
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger l'historique (CSV)", csv, "historique_mga.csv", "text/csv")