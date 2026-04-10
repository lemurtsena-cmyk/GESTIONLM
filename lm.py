import streamlit as st
import sqlite3, pandas as pd
from datetime import datetime
import os

DB = "gestion_tables_mga.db"

# --- CONFIGURATION ET UTILS ---
st.set_page_config(page_title="Melamine & Metallique", layout="wide", page_icon="🏗️")

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
    # Migration auto si colonne manquante
    try:
        c.execute("ALTER TABLE produits ADD COLUMN forme_pieds TEXT")
    except:
        pass
    c.commit()

init_db()
conn = get_conn()

# --- BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo mm.jpg"):
        st.image("logo mm.jpg", use_container_width=True)
    else:
        st.title("🏗️ Melamine & Metallique")
    
    st.divider()
    page = st.radio("Menu", ["Tableau de bord", "Produits", "Entrées Stock", "Ventes", "Journalier", "Comptabilité"])
    st.sidebar.caption("By Lemur tsena")

# --- TABLEAU DE BORD ---
if page=="Tableau de bord":
    st.header("📊 Tableau de bord")
    prod = pd.read_sql("SELECT * FROM produits", conn)
    valeur_stock = (prod["stock"] * prod["prix_achat"]).sum()
    
    mois_actuel = datetime.now().strftime("%Y-%m") + "%"
    v_prod = pd.read_sql("SELECT SUM(qte*pu) as val FROM mouvements WHERE type='VENTE' AND date LIKE ?", conn, params=(mois_actuel,)).val[0] or 0
    r_jour = pd.read_sql("SELECT SUM(montant) as val FROM journal WHERE type='RECETTE' AND date LIKE ?", conn, params=(mois_actuel,)).val[0] or 0
    total_recettes = v_prod + r_jour
    
    a_prod = pd.read_sql("SELECT SUM(qte*pu) as val FROM mouvements WHERE type='ACHAT' AND date LIKE ?", conn, params=(mois_actuel,)).val[0] or 0
    d_jour = pd.read_sql("SELECT SUM(montant) as val FROM journal WHERE type='DEPENSE' AND date LIKE ?", conn, params=(mois_actuel,)).val[0] or 0
    total_depenses = a_prod + d_jour

    c1,c2,c3 = st.columns(3)
    c1.metric("Valeur du stock", mga(valeur_stock))
    c2.metric("Recettes (Mois)", mga(total_recettes))
    c3.metric("Bénéfice Net (Mois)", mga(total_recettes - total_depenses))
    
    st.subheader("📦 État des stocks")
    st.dataframe(prod[["code","nom","stock","longueur","largeur","hauteur","forme_pieds"]], use_container_width=True)

# --- PRODUITS ---
elif page=="Produits":
    st.header("📦 Catalogue des Produits")
    df = pd.read_sql("SELECT * FROM produits", conn)
    
    # Affichage sans prix d'achat
    df_view = df.drop(columns=['prix_achat'])
    df_view['prix_vente'] = df_view['prix_vente'].apply(mga)
    st.dataframe(df_view, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Nouveau Produit"):
            with st.form("add_prod"):
                nom = st.text_input("Nom du modèle")
                c1,c2,c3 = st.columns(3)
                cat = c1.selectbox("Catégorie", ["TABLE", "CHAISE", "BUREAU", "ETAGERE", "AUTRE"])
                coul = c2.text_input("Couleur")
                pieds = c3.text_input("Forme pieds")
                
                c1,c2,c3 = st.columns(3)
                long = c1.number_input("Longueur (cm)", 0)
                larg = c2.number_input("Largeur (cm)", 0)
                haut = c3.number_input("Hauteur (cm)", 0)
                
                c1,c2 = st.columns(2)
                pa = c1.number_input("Prix d'achat (Ar)", 0)
                pv = c2.number_input("Prix de vente (Ar)", 0)
                stock = st.number_input("Stock initial", 0)
                
                if st.form_submit_button("Enregistrer"):
                    # CODE AUTO: CATEGORIE-LONG-LARG-HAUT-COUL-PIEDS
                    code_auto = f"{cat}-{long}-{larg}-{haut}-{coul}-{pieds}".upper().replace(" ", "")
                    try:
                        conn.execute("""INSERT INTO produits 
                            (code, nom, categorie, hauteur, longueur, largeur, couleur, forme_pieds, prix_achat, prix_vente, stock) 
                            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                            (code_auto, nom, cat, haut, long, larg, coul, pieds, pa, pv, stock))
                        conn.commit()
                        st.success(f"Produit créé : {code_auto}")
                        st.rerun()
                    except:
                        st.error("Erreur : Ce code existe déjà ou les données sont invalides.")

    with col2:
        with st.expander("📝 Modifier / Supprimer"):
            if not df.empty:
                p_edit = st.selectbox("Produit à modifier", df.itertuples(), format_func=lambda x: f"{x.code} - {x.nom}")
                with st.form("edit_prod"):
                    n_nom = st.text_input("Nom", value=p_edit.nom)
                    n_pv = st.number_input("Prix Vente", value=int(p_edit.prix_vente))
                    n_stock = st.number_input("Stock", value=int(p_edit.stock))
                    
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 Mettre à jour"):
                        conn.execute("UPDATE produits SET nom=?, prix_vente=?, stock=? WHERE id=?", (n_nom, n_pv, n_stock, p_edit.id))
                        conn.commit(); st.rerun()
                    if b2.form_submit_button("🗑️ Supprimer"):
                        conn.execute("DELETE FROM produits WHERE id=?", (p_edit.id,))
                        conn.commit(); st.rerun()

# --- ENTREES STOCK ---
elif page=="Entrées Stock":
    st.header("📥 Entrée de Marchandise")
    prod = pd.read_sql("SELECT id, code, nom FROM produits", conn)
    four = pd.read_sql("SELECT * FROM fournisseurs", conn)
    with st.form("entree"):
        p = st.selectbox("Produit", prod.itertuples(), format_func=lambda x:f"{x.code} - {x.nom}")
        f = st.selectbox("Fournisseur", four.itertuples(), format_func=lambda x:x.nom)
        qte = st.number_input("Quantité", 1)
        pu = st.number_input("Prix unitaire achat (Ar)", 0)
        if st.form_submit_button("Valider l'achat"):
            conn.execute("INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers) VALUES (?,?,?,?,?,?)",
                         (datetime.now().isoformat(), p.id, 'ACHAT', qte, pu, f.nom))
            conn.execute("UPDATE produits SET stock=stock+?, prix_achat=? WHERE id=?",(qte, pu, p.id))
            conn.commit(); st.success("Stock mis à jour !")

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
                conn.commit(); st.balloons()
    else:
        st.warning("Aucun stock disponible.")

# --- JOURNALIER ---
elif page=="Journalier":
    st.header("📒 Ventes et Dépenses Journalières")
    df_j = pd.read_sql("SELECT id, date, type, description, montant FROM journal ORDER BY date DESC", conn)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        t_add, t_edit = st.tabs(["➕ Ajouter", "📝 Modifier / Suppr"])
        with t_add:
            with st.form("add_j"):
                typ = st.selectbox("Type", ["DEPENSE", "RECETTE"])
                des = st.text_input("Description")
                mnt = st.number_input("Montant (Ar)", 0)
                dat = st.date_input("Date", datetime.now())
                if st.form_submit_button("Enregistrer"):
                    conn.execute("INSERT INTO journal(date,type,description,montant) VALUES (?,?,?,?)", (dat.isoformat(), typ, des, mnt))
                    conn.commit(); st.rerun()
        with t_edit:
            if not df_j.empty:
                item = st.selectbox("Opération", df_j.itertuples(), format_func=lambda x: f"{x.date} | {x.description}")
                with st.form("edit_j"):
                    e_des = st.text_input("Description", value=item.description)
                    e_mnt = st.number_input("Montant", value=int(item.montant))
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 Maj"):
                        conn.execute("UPDATE journal SET description=?, montant=? WHERE id=?", (e_des, e_mnt, item.id))
                        conn.commit(); st.rerun()
                    if b2.form_submit_button("🗑️ Suppr"):
                        conn.execute("DELETE FROM journal WHERE id=?", (item.id,))
                        conn.commit(); st.rerun()

    with col2:
        st.dataframe(df_j.drop(columns=['id']), use_container_width=True)

# --- COMPTABILITÉ ---
else:
    st.header("💰 Comptabilité")
    mouv = pd.read_sql("SELECT type, (qte*pu) as montant FROM mouvements", conn)
    jour = pd.read_sql("SELECT type, montant FROM journal", conn)
    
    recettes = mouv[mouv.type=='VENTE']["montant"].sum() + jour[jour.type=='RECETTE']["montant"].sum()
    depenses = mouv[mouv.type=='ACHAT']["montant"].sum() + jour[jour.type=='DEPENSE']["montant"].sum()
    
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Recettes", mga(recettes))
    c2.metric("Total Dépenses", mga(depenses))
    c3.metric("Profit Global", mga(recettes - depenses))
    
    # Graphique
    m_plot = pd.read_sql("SELECT substr(date,1,10) as date, (qte*pu) as montant, type FROM mouvements", conn)
    j_plot = pd.read_sql("SELECT substr(date,1,10) as date, montant, type FROM journal", conn)
    total_data = pd.concat([m_plot, j_plot])
    if not total_data.empty:
        total_data['valeur'] = total_data.apply(lambda x: x['montant'] if x['type'] in ['VENTE', 'RECETTE'] else -x['montant'], axis=1)
        st.line_chart(total_data.groupby('date')['valeur'].sum())
