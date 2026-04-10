import streamlit as st
import sqlite3, pandas as pd
from datetime import datetime

DB = "gestion_tables_mga.db"

# --- Utils ---
def mga(x): 
    return f"{int(x or 0):,}".replace(",", " ") + " Ar"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    c = get_conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS produits(
        id INTEGER PRIMARY KEY, code TEXT UNIQUE, nom TEXT, categorie TEXT,
        materiau TEXT, longueur INTEGER, largeur INTEGER, couleur TEXT,
        prix_achat INTEGER, prix_vente INTEGER, stock INTEGER DEFAULT 0, stock_min INTEGER DEFAULT 2
    );
    CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY, nom TEXT, tel TEXT);
    CREATE TABLE IF NOT EXISTS fournisseurs(id INTEGER PRIMARY KEY, nom TEXT, tel TEXT);
    CREATE TABLE IF NOT EXISTS mouvements(
        id INTEGER PRIMARY KEY, date TEXT, produit_id INTEGER, type TEXT,
        qte INTEGER, pu INTEGER, tiers TEXT, ref TEXT
    );
    """)
    # données démo si vide
    df = pd.read_sql("SELECT COUNT(*) as n FROM produits", c)
    if df.n[0]==0:
        c.execute("INSERT INTO produits(code,nom,categorie,materiau,longueur,largeur,couleur,prix_achat,prix_vente,stock,stock_min) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  ("TBL-MANG-160","Table à manger 6 pers","Salle à manger","Bois",160,90,"Marron",350000,520000,3,2))
        c.execute("INSERT INTO produits VALUES (NULL,'TBL-BUR-120','Table bureau 120','Bureau','Métal/Bois',120,60,'Noir',180000,250000,5,2)")
        c.execute("INSERT INTO fournisseurs(nom) VALUES ('Menuiserie Andry'),('Import Tana')")
        c.execute("INSERT INTO clients(nom) VALUES ('Particulier'),('Hotel Sakura')")
    c.commit()

init_db()
conn = get_conn()

st.set_page_config(page_title="Stock Tables MGA", layout="wide", page_icon="🪑")
st.sidebar.title("🪑 Vente de Tables")
page = st.sidebar.radio("Menu", ["Tableau de bord","Produits","Entrées Stock","Ventes","Comptabilité"])

# --- TABLEAU DE BORD ---
if page=="Tableau de bord":
    st.header("Tableau de bord")
    prod = pd.read_sql("SELECT * FROM produits", conn)
    prod["valeur_stock"] = prod["stock"] * prod["prix_achat"]
    valeur = prod["valeur_stock"].sum()
    
    ventes_mois = pd.read_sql("SELECT SUM(qte*pu) as ca FROM mouvements WHERE type='VENTE' AND date LIKE ?", conn, params=(datetime.now().strftime("%Y-%m")+"%",))
    ca = ventes_mois.ca[0] or 0
    
    achats_mois = pd.read_sql("SELECT SUM(qte*pu) as achat FROM mouvements WHERE type='ACHAT' AND date LIKE ?", conn, params=(datetime.now().strftime("%Y-%m")+"%",))
    achat = achats_mois.achat[0] or 0

    c1,c2,c3 = st.columns(3)
    c1.metric("Valeur du stock", mga(valeur))
    c2.metric("CA du mois", mga(ca))
    c3.metric("Bénéfice brut", mga(ca-achat), delta_color="normal")
    
    alertes = prod[prod.stock <= prod.stock_min]
    st.subheader("⚠️ À réapprovisionner")
    st.dataframe(alertes[["code","nom","stock","stock_min"]], use_container_width=True)

# --- PRODUITS ---
elif page=="Produits":
    st.header("Catalogue Tables")
    df = pd.read_sql("SELECT * FROM produits", conn)
    st.dataframe(df.assign(prix_achat=df.prix_achat.apply(mga), prix_vente=df.prix_vente.apply(mga)), use_container_width=True)
    
    with st.expander("➕ Ajouter une table"):
        with st.form("add"):
            c1,c2,c3 = st.columns(3)
            code=c1.text_input("Code"); nom=c2.text_input("Nom"); cat=c3.selectbox("Catégorie",["Salle à manger","Bureau","Basse","Pliante","Enfant"])
            c1,c2,c3 = st.columns(3)
            mat=c1.text_input("Matériau"); long=c2.number_input("Longueur cm",60,300,120); larg=c3.number_input("Largeur cm",40,150,80)
            coul=st.text_input("Couleur")
            pa=st.number_input("Prix d'achat (Ar)",0, step=1000); pv=st.number_input("Prix de vente (Ar)",0, step=1000)
            stock=st.number_input("Stock initial",0); smin=st.number_input("Stock alerte",0,2)
            if st.form_submit_button("Enregistrer"):
                conn.execute("INSERT INTO produits VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)",(code,nom,cat,mat,long,larg,coul,pa,pv,stock,smin))
                conn.commit(); st.success("Produit ajouté !"); st.rerun()

# --- ENTREES ---
elif page=="Entrées Stock":
    st.header("📥 Entrée stock (Achat fournisseur)")
    prod = pd.read_sql("SELECT id, code, nom FROM produits", conn)
    four = pd.read_sql("SELECT * FROM fournisseurs", conn)
    with st.form("entree"):
        p = st.selectbox("Produit", prod.itertuples(), format_func=lambda x:f"{x.code} - {x.nom}")
        f = st.selectbox("Fournisseur", four.itertuples(), format_func=lambda x:x.nom)
        qte = st.number_input("Quantité",1); pu = st.number_input("Prix unitaire achat (Ar)",0, step=1000)
        if st.form_submit_button("Valider entrée"):
            conn.execute("INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers) VALUES (?,?,?,?,?,?)",
                         (datetime.now().isoformat(), p.id, 'ACHAT', qte, pu, f.nom))
            conn.execute("UPDATE produits SET stock=stock+?, prix_achat=? WHERE id=?",(qte, pu, p.id))
            conn.commit(); st.success(f"Stock mis à jour: +{qte}")

# --- VENTES ---
elif page=="Ventes":
    st.header("📤 Vente client")
    prod = pd.read_sql("SELECT * FROM produits WHERE stock>0", conn)
    cli = pd.read_sql("SELECT * FROM clients", conn)
    with st.form("vente"):
        p = st.selectbox("Produit", prod.itertuples(), format_func=lambda x:f"{x.code} - {x.nom} (Stock:{x.stock} | {mga(x.prix_vente)})")
        c = st.selectbox("Client", cli.itertuples(), format_func=lambda x:x.nom)
        qte = st.number_input("Quantité",1, max_value=int(p.stock))
        pu = st.number_input("Prix vente (Ar)", int(p.prix_vente), step=1000)
        if st.form_submit_button("Facturer"):
            total = qte*pu
            ref = f"V{datetime.now().strftime('%y%m%d%H%M')}"
            conn.execute("INSERT INTO mouvements(date,produit_id,type,qte,pu,tiers,ref) VALUES (?,?,?,?,?,?,?)",
                         (datetime.now().isoformat(), p.id, 'VENTE', qte, pu, c.nom, ref))
            conn.execute("UPDATE produits SET stock=stock-? WHERE id=?",(qte, p.id))
            conn.commit()
            st.success(f"Vente {ref} enregistrée - Total: {mga(total)}")
            st.balloons()

    st.subheader("Dernières ventes")
    v = pd.read_sql("SELECT date,ref,tiers,qte,pu,qte*pu as total FROM mouvements WHERE type='VENTE' ORDER BY id DESC LIMIT 20", conn)
    v["total"] = v["total"].apply(mga); v["pu"] = v["pu"].apply(mga)
    st.dataframe(v, use_container_width=True)

# --- COMPTA ---
else:
    st.header("💰 Comptabilité simplifiée (MGA)")
    mouv = pd.read_sql("SELECT * FROM mouvements", conn)
    if not mouv.empty:
        mouv["montant"] = mouv["qte"]*mouv["pu"]
        ca = mouv[mouv.type=='VENTE']["montant"].sum()
        achat = mouv[mouv.type=='ACHAT']["montant"].sum()
        benef = ca - achat
        c1,c2,c3 = st.columns(3)
        c1.metric("Recettes totales", mga(ca))
        c2.metric("Achats totaux", mga(achat))
        c3.metric("Bénéfice", mga(benef))
        st.line_chart(mouv.groupby(mouv.date.str[:10])["montant"].sum())
    else:
        st.info("Pas encore de mouvements")