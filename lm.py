import streamlit as st
import sqlite3, pandas as pd
from datetime import datetime
import os

DB = "gestion_tables_mga.db"

# --- Utils ---
def mga(x): 
    return f"{int(x or 0):,}".replace(",", " ") + " Ar"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    c = get_conn()
    # Mise à jour du schéma : materiau -> hauteur, suppression stock_min
    c.executescript("""
    CREATE TABLE IF NOT EXISTS produits(
        id INTEGER PRIMARY KEY, code TEXT UNIQUE, nom TEXT, categorie TEXT,
        hauteur INTEGER, longueur INTEGER, largeur INTEGER, couleur TEXT,
        prix_achat INTEGER, prix_vente INTEGER, stock INTEGER DEFAULT 0
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
    
    # Données initiales si vide
    df = pd.read_sql("SELECT COUNT(*) as n FROM produits", c)
    if df.n[0]==0:
        c.execute("INSERT INTO produits(code,nom,categorie,hauteur,longueur,largeur,couleur,prix_achat,prix_vente,stock) VALUES (?,?,?,?,?,?,?,?,?,?)",
                  ("TBL-MANG-160","Table à manger 6 pers","Salle à manger",75,160,90,"Marron",350000,520000,3))
        c.execute("INSERT INTO fournisseurs(nom) VALUES ('Menuiserie Andry'),('Import Tana')")
        c.execute("INSERT INTO clients(nom) VALUES ('Particulier'),('Hotel Sakura')")
    c.commit()

init_db()
conn = get_conn()

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Melamine & Metallique", layout="wide", page_icon="🏗️")

# --- BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo mm.jpg"):
        st.image("logo mm.jpg", use_container_width=True)
    else:
        st.title("🏗️ Melamine & Metallique")
    
    st.divider()
    page = st.radio("Menu de gestion", ["Tableau de bord", "Produits", "Entrées Stock", "Ventes", "Journalier", "Comptabilité"])
    st.sidebar.caption("By Lemur tsena")

# --- TABLEAU DE BORD ---
if page=="Tableau de bord":
    st.header("📊 Tableau de bord")
    
    # Calculs Stock
    prod = pd.read_sql("SELECT * FROM produits", conn)
    valeur_stock = (prod["stock"] * prod["prix_achat"]).sum()
    
    # Calculs Flux (Mouvements + Journal)
    mois_actuel = datetime.now().strftime("%Y-%m") + "%"
    
    # Recettes (Ventes produits + Recettes journalières)
    v_prod = pd.read_sql("SELECT SUM(qte*pu) as val FROM mouvements WHERE type='VENTE' AND date LIKE ?", conn, params=(mois_actuel,)).val[0] or 0
    r_jour = pd.read_sql("SELECT SUM(montant) as val FROM journal WHERE type='RECETTE' AND date LIKE ?", conn, params=(mois_actuel,)).val[0] or 0
    total_recettes = v_prod + r_jour
    
    # Dépenses (Achats produits + Dépenses journalières)
    a_prod = pd.read_sql("SELECT SUM(qte*pu) as val FROM mouvements WHERE type='ACHAT' AND date LIKE ?", conn, params=(mois_actuel,)).val[0] or 0
    d_jour = pd.read_sql("SELECT SUM(montant) as val FROM journal WHERE type='DEPENSE' AND date LIKE ?", conn, params=(mois_actuel,)).val[0] or 0
    total_depenses = a_prod + d_jour

    c1,c2,c3 = st.columns(3)
    c1.metric("Valeur du stock", mga(valeur_stock))
    c2.metric("Recettes (Mois)", mga(total_recettes))
    c3.metric("Bénéfice Net estimé", mga(total_recettes - total_depenses))
    
    st.subheader("📦 État des stocks")
    st.dataframe(prod[["code","nom","stock","hauteur","longueur","largeur"]], use_container_width=True)

# --- PRODUITS ---
elif page=="Produits":
    st.header("📦 Catalogue des Produits")
    df = pd.read_sql("SELECT * FROM produits", conn)
    st.dataframe(df.assign(prix_achat=df.prix_achat.apply(mga), prix_vente=df.prix_vente.apply(mga)), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Nouveau Produit"):
            with st.form("add"):
                c1,c2,c3 = st.columns(3)
                code=c1.text_input("Code"); nom=c2.text_input("Nom"); cat=c3.selectbox("Catégorie",["Table","Chaise","Bureau","Etagère","Autre"])
                c1,c2,c3 = st.columns(3)
                haut=c1.number_input("Hauteur cm",0); long=c2.number_input("Longueur cm",0); larg=c3.number_input("Largeur cm",0)
                coul=st.text_input("Couleur")
                pa=st.number_input("Prix d'achat (Ar)",0); pv=st.number_input("Prix de vente (Ar)",0)
                stock=st.number_input("Stock initial",0)
                if st.form_submit_button("Enregistrer"):
                    conn.execute("INSERT INTO produits (code,nom,categorie,hauteur,longueur,largeur,couleur,prix_achat,prix_vente,stock) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                 (code,nom,cat,haut,long,larg,coul,pa,pv,stock))
                    conn.commit(); st.success("Ajouté !"); st.rerun()
    
    with col2:
        with st.expander("📝 Modifier Stock / Prix"):
            if not df.empty:
                p_to_edit = st.selectbox("Choisir le produit", df.itertuples(), format_func=lambda x: f"{x.code} - {x.nom}")
                with st.form("edit"):
                    n_stock = st.number_input("Nouveau Stock", value=int(p_to_edit.stock))
                    n_pa = st.number_input("Prix Achat (Ar)", value=int(p_to_edit.prix_achat))
                    n_pv = st.number_input("Prix Vente (Ar)", value=int(p_to_edit.prix_vente))
                    if st.form_submit_button("Mettre à jour"):
                        conn.execute("UPDATE produits SET stock=?, prix_achat=?, prix_vente=? WHERE id=?", (n_stock, n_pa, n_pv, p_to_edit.id))
                        conn.commit(); st.success("Mis à jour !"); st.rerun()

# --- ENTREES ---
elif page=="Entrées Stock":
    st.header("📥 Entrée de Marchandise")
    prod = pd.read_sql("SELECT id, code, nom FROM produits", conn)
    four = pd.read_sql("SELECT * FROM fournisseurs", conn)
    with st.form("entree"):
        p = st.selectbox("Produit", prod.itertuples(), format_func=lambda x:f"{x.code} - {x.nom}")
        f = st.selectbox("Fournisseur", four.itertuples(), format_func=lambda x:x.nom)
        qte = st.number_input("Quantité",1); pu = st.number_input("Prix unitaire achat (Ar)",0)
        if st.form_submit_button("Valider l'achat"):
            conn.execute("INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers) VALUES (?,?,?,?,?,?)",
                         (datetime.now().isoformat(), p.id, 'ACHAT', qte, pu, f.nom))
            conn.execute("UPDATE produits SET stock=stock+?, prix_achat=? WHERE id=?",(qte, pu, p.id))
            conn.commit(); st.success(f"Stock augmenté de {qte}")

# --- VENTES ---
elif page=="Ventes":
    st.header("📤 Vente / Facturation")
    prod = pd.read_sql("SELECT * FROM produits WHERE stock>0", conn)
    cli = pd.read_sql("SELECT * FROM clients", conn)
    if not prod.empty:
        with st.form("vente"):
            p = st.selectbox("Produit", prod.itertuples(), format_func=lambda x:f"{x.code} (Stock:{x.stock})")
            c = st.selectbox("Client", cli.itertuples(), format_func=lambda x:x.nom)
            qte = st.number_input("Quantité", 1, max_value=int(p.stock))
            pu = st.number_input("Prix vente (Ar)", int(p.prix_vente))
            if st.form_submit_button("Enregistrer la vente"):
                ref = f"V{datetime.now().strftime('%y%m%d%H%M')}"
                conn.execute("INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers,ref) VALUES (?,?,?,?,?,?,?)",
                             (datetime.now().isoformat(), p.id, 'VENTE', qte, pu, c.nom, ref))
                conn.execute("UPDATE produits SET stock=stock-? WHERE id=?",(qte, p.id))
                conn.commit(); st.success(f"Vente {ref} effectuée !"); st.balloons()
    else:
        st.warning("Plus de stock disponible pour la vente.")

# --- JOURNALIER (NOUVEAU) ---
elif page=="Journalier":
    st.header("📒 Ventes et Dépenses Journalières")
    st.info("Utilisez cette section pour les frais divers (loyer, transport, snacks) ou recettes hors produits.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("journal"):
            t_type = st.selectbox("Type", ["DEPENSE", "RECETTE"])
            desc = st.text_input("Description (ex: Transport, Petit déjeuner)")
            montant = st.number_input("Montant (Ar)", min_value=0, step=500)
            date_j = st.date_input("Date", datetime.now())
            if st.form_submit_button("Enregistrer"):
                conn.execute("INSERT INTO journal(date, type, description, montant) VALUES (?,?,?,?)",
                             (date_j.isoformat(), t_type, desc, montant))
                conn.commit(); st.success("Enregistré !"); st.rerun()
    
    with col2:
        df_j = pd.read_sql("SELECT date, type, description, montant FROM journal ORDER BY date DESC LIMIT 20", conn)
        st.subheader("Dernières opérations")
        st.table(df_j)

# --- COMPTA ---
else:
    st.header("💰 Comptabilité")
    
    # Données Mouvements (Produits)
    mouv = pd.read_sql("SELECT type, (qte*pu) as montant FROM mouvements", conn)
    # Données Journal (Divers)
    jour = pd.read_sql("SELECT type, montant FROM journal", conn)
    
    # Calculs croisés
    recettes_total = mouv[mouv.type=='VENTE']["montant"].sum() + jour[jour.type=='RECETTE']["montant"].sum()
    depenses_total = mouv[mouv.type=='ACHAT']["montant"].sum() + jour[jour.type=='DEPENSE']["montant"].sum()
    
    c1,c2,c3 = st.columns(3)
    c1.metric("Recettes Totales", mga(recettes_total))
    c2.metric("Dépenses Totales", mga(depenses_total))
    c3.metric("Solde (Profit)", mga(recettes_total - depenses_total))
    
    st.subheader("Historique global (Flux journaliers + Ventes)")
    # Fusion des données pour graphique
    m_plot = pd.read_sql("SELECT substr(date,1,10) as date, (qte*pu) as montant, type FROM mouvements", conn)
    j_plot = pd.read_sql("SELECT substr(date,1,10) as date, montant, type FROM journal", conn)
    
    total_data = pd.concat([m_plot, j_plot])
    if not total_data.empty:
        # On traite les dépenses comme négatives pour le graphique
        total_data['valeur'] = total_data.apply(lambda x: x['montant'] if x['type'] in ['VENTE', 'RECETTE'] else -x['montant'], axis=1)
        chart_data = total_data.groupby('date')['valeur'].sum()
        st.line_chart(chart_data)