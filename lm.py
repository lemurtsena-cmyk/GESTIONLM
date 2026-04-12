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
    # Tables de base
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
        qte INTEGER, pu INTEGER, tiers TEXT, ref TEXT, mode TEXT
    );
    CREATE TABLE IF NOT EXISTS journal(
        id INTEGER PRIMARY KEY, date TEXT, type TEXT, description TEXT, montant INTEGER, mode TEXT
    );
    CREATE TABLE IF NOT EXISTS commandes(
        id INTEGER PRIMARY KEY, date TEXT, client TEXT, description TEXT, 
        total INTEGER, avance INTEGER, mode TEXT
    );
    """)
    # Migration pour ajouter la colonne 'mode' si elle n'existe pas (Ventes/Journal)
    for table in ["mouvements", "journal"]:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN mode TEXT DEFAULT 'ESPECE'")
        except: pass
    c.commit()

init_db()
conn = get_conn()

# --- LISTES DE CHOIX ---
LISTE_PIEDS = ["/U", "/V", "/X", "/K", "/PLIABLE", "/TABOURET CARRE", "/TABOURET CERCLE"]
LISTE_COULEURS = [
    "/BLANC UNIS", "/NOIR UNIS", "/GRIS MARBRE", "#1023", "#1025", "#805", 
    "#806", "#506", "#16854", "#16855", "#1010", "#8042", "#8052", 
    "#932", "#809", "#308 BM", "#7058", "#76-1"
]
LISTE_MODES = ["ESPECE", "MVOLA", "ORANGEMONEY", "BANQUE", "AUTRE"]

# --- BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo mm.jpg"):
        st.image("logo mm.jpg", use_container_width=True)
    else:
        st.title("🏗️ Melamine & Metallique")
    
    st.divider()
    page = st.radio("Menu", ["Tableau de bord", "Produits", "Entrées Stock", "Ventes", "Commandes Spéciales", "Journalier", "Comptabilité"])
    st.sidebar.caption("By Lemur tsena")

# --- TABLEAU DE BORD ---
if page=="Tableau de bord":
    st.header("📊 Tableau de bord")
    prod = pd.read_sql("SELECT * FROM produits", conn)
    valeur_stock = (prod["stock"] * prod["prix_vente"]).sum()
    
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
    
    df_view = df.drop(columns=['prix_achat'])
    df_view['prix_vente'] = df_view['prix_vente'].apply(mga)
    st.dataframe(df_view, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("➕ Nouveau Produit"):
            with st.form("add_prod"):
                c1,c2,c3 = st.columns(3)
                cat = c1.selectbox("Catégorie", ["TABLE", "CHAISE", "BUREAU", "ETAGERE", "AUTRE"])
                coul = c2.selectbox("Couleur", LISTE_COULEURS)
                pieds = c3.selectbox("Forme pieds", LISTE_PIEDS)
                long = c1.number_input("Longueur (cm)", 0)
                larg = c2.number_input("Largeur (cm)", 0)
                haut = c3.number_input("Hauteur (cm)", 0)
                pa = st.number_input("Prix d'achat (Ar)", 0)
                pv = st.number_input("Prix de vente (Ar)", 0)
                stock = st.number_input("Stock initial", 0)
                
                if st.form_submit_button("Enregistrer"):
                    nom_auto = f"{cat}.{long}.{larg}.{pieds}"
                    c_clean = coul.replace("/", "").replace("#", "")
                    p_clean = pieds.replace("/", "")
                    code_auto = f"{cat}-{long}-{larg}-{haut}-{c_clean}-{p_clean}".upper().replace(" ", "")
                    try:
                        conn.execute("INSERT INTO produits (code, nom, categorie, hauteur, longueur, largeur, couleur, forme_pieds, prix_achat, prix_vente, stock) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                            (code_auto, nom_auto, cat, haut, long, larg, coul, pieds, pa, pv, stock))
                        conn.commit(); st.success(f"Produit créé"); st.rerun()
                    except: st.error("Erreur : Code déjà existant.")

# --- ENTREES STOCK ---
elif page=="Entrées Stock":
    st.header("📥 Entrée de Marchandise")
    prod = pd.read_sql("SELECT id, code, nom FROM produits", conn)
    with st.form("entree"):
        p = st.selectbox("Produit", prod.itertuples(), format_func=lambda x:f"{x.nom} ({x.code})")
        qte = st.number_input("Quantité", 1)
        pu = st.number_input("Prix unitaire achat (Ar)", 0)
        mode = st.selectbox("Mode de Paiement (Sortie d'argent)", LISTE_MODES)
        tier = st.text_input("Fournisseur", "Divers")
        if st.form_submit_button("Valider l'achat"):
            conn.execute("INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers,mode) VALUES (?,?,?,?,?,?,?)",
                         (datetime.now().isoformat(), p.id, 'ACHAT', qte, pu, tier, mode))
            conn.execute("UPDATE produits SET stock=stock+?, prix_achat=? WHERE id=?",(qte, pu, p.id))
            conn.commit(); st.success("Stock mis à jour !")

# --- VENTES ---
elif page=="Ventes":
    st.header("📤 Vente Directe")
    prod = pd.read_sql("SELECT * FROM produits WHERE stock>0", conn)
    if not prod.empty:
        with st.form("vente"):
            p = st.selectbox("Produit", prod.itertuples(), format_func=lambda x:f"{x.nom} (Stock:{x.stock})")
            client = st.text_input("Client", "Anonyme")
            qte = st.number_input("Quantité", 1, max_value=int(p.stock))
            pu = st.number_input("Prix vente (Ar)", int(p.prix_vente))
            mode = st.selectbox("Mode de Paiement (Encaissement)", LISTE_MODES)
            if st.form_submit_button("Enregistrer la vente"):
                ref = f"V{datetime.now().strftime('%y%m%d%H%M')}"
                conn.execute("INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers,ref,mode) VALUES (?,?,?,?,?,?,?,?)",
                             (datetime.now().isoformat(), p.id, 'VENTE', qte, pu, client, ref, mode))
                conn.execute("UPDATE produits SET stock=stock-? WHERE id=?",(qte, p.id))
                conn.commit(); st.balloons(); st.rerun()
    else:
        st.warning("Aucun stock disponible.")

# --- COMMANDES SPECIALES ---
elif page=="Commandes Spéciales":
    st.header("📝 Commandes Spéciales (Sur mesure)")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("cmd_form"):
            st.subheader("Nouvelle Commande")
            client = st.text_input("Client")
            desc = st.text_area("Description du projet")
            total = st.number_input("Montant Total (Ar)", 0)
            avance = st.number_input("Avance payée (Ar)", 0)
            mode = st.selectbox("Mode de paiement avance", LISTE_MODES)
            if st.form_submit_button("Enregistrer la commande"):
                conn.execute("INSERT INTO commandes(date, client, description, total, avance, mode) VALUES (?,?,?,?,?,?)",
                             (datetime.now().strftime("%Y-%m-%d"), client, desc, total, avance, mode))
                # On ajoute l'avance dans le journal comme recette
                conn.execute("INSERT INTO journal(date, type, description, montant, mode) VALUES (?,?,?,?,?)",
                             (datetime.now().isoformat(), "RECETTE", f"Avance CMD: {client}", avance, mode))
                conn.commit(); st.success("Commande enregistrée !"); st.rerun()

    with col2:
        df_c = pd.read_sql("SELECT * FROM commandes ORDER BY id DESC", conn)
        if not df_c.empty:
            df_c['Reste à payer'] = df_c['total'] - df_c['avance']
            # Formatage pour affichage
            df_show = df_c.copy()
            for col in ['total', 'avance', 'Reste à payer']:
                df_show[col] = df_show[col].apply(mga)
            st.dataframe(df_show, use_container_width=True)
            
            with st.expander("Supprimer une commande"):
                id_del = st.number_input("ID à supprimer", min_value=1, step=1)
                if st.button("Confirmer Suppression"):
                    conn.execute("DELETE FROM commandes WHERE id=?", (id_del,))
                    conn.commit(); st.rerun()

# --- JOURNALIER ---
elif page=="Journalier":
    st.header("📒 Journal des opérations (Dépenses / Recettes)")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("add_j"):
            typ = st.selectbox("Type", ["DEPENSE", "RECETTE"])
            des = st.text_input("Description / Motif")
            mnt = st.number_input("Montant (Ar)", 0)
            mode = st.selectbox("Mode", LISTE_MODES)
            dat = st.date_input("Date", datetime.now())
            if st.form_submit_button("Enregistrer"):
                conn.execute("INSERT INTO journal(date,type,description,montant,mode) VALUES (?,?,?,?,?)", 
                             (dat.isoformat(), typ, des, mnt, mode))
                conn.commit(); st.rerun()

    with col2:
        df_j = pd.read_sql("SELECT date, type, description, mode, montant FROM journal ORDER BY date DESC", conn)
        st.dataframe(df_j, use_container_width=True)

# --- COMPTABILITÉ ---
else:
    st.header("💰 État des Caisses et Comptabilité")
    
    # Calcul des soldes par caisse
    mouv = pd.read_sql("SELECT type, (qte*pu) as mnt, mode FROM mouvements", conn)
    jour = pd.read_sql("SELECT type, montant as mnt, mode FROM journal", conn)
    all_trans = pd.concat([mouv, jour])

    st.subheader("🏦 Solde par mode de paiement")
    cols = st.columns(len(LISTE_MODES))
    for i, m in enumerate(LISTE_MODES):
        rec = all_trans[(all_trans.mode == m) & (all_trans.type.isin(['VENTE', 'RECETTE']))]['mnt'].sum()
        dep = all_trans[(all_trans.mode == m) & (all_trans.type.isin(['ACHAT', 'DEPENSE']))]['mnt'].sum()
        solde = rec - dep
        cols[i].metric(m, mga(solde))

    st.divider()
    recettes = all_trans[all_trans.type.isin(['VENTE', 'RECETTE'])]['mnt'].sum()
    depenses = all_trans[all_trans.type.isin(['ACHAT', 'DEPENSE'])]['mnt'].sum()
    
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Recettes", mga(recettes))
    c2.metric("Total Dépenses", mga(depenses))
    c3.metric("Bénéfice Global", mga(recettes - depenses), delta_color="normal")
