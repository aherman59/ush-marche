import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

####

# UTILS

####


conn = sqlite3.connect("indicateurs_OLS.sqlite3")


TYPES =  {
    "Regions": "region",
    "Principales métropoles": "epci",
    "Zonage ABC": "zonage_ABC",
    "Zonage 123 ": "zonage_123",
}

famille = "Tout OLS"
type_perimetre = "region"
perimetre = None 
typo = "Foncier Nu"

CATEGORIES = [
    {"code": "P1", "valeur": "ETAT"},
    {"code": "P2", "valeur": "REGION"},
    {"code": "P3", "valeur": "DEPARTEMENT"},
    {"code": "P4", "valeur": "INTERCOMMUNALITE"},
    {"code": "P5", "valeur": "COMMUNE"},
    {"code": "P6", "valeur": "COLLECTIVITE TERRITORIALE AUTRE"},
    {"code": "P0", "valeur": "AUTRE PERSONNE MORALE PUBLIQUE"},
    {"code": "F1", "valeur": "ORGANISME LOGEMENT SOCIAL"},
    {"code": "F2", "valeur": "ETABLISSEMENT PUBLIC FONCIER"},
    {"code": "A4", "valeur": "SAFER"},
    {"code": "F4", "valeur": "SEM / SPLA"},
    {"code": "F5", "valeur": "AMENAGEUR FONCIER"},
    {"code": "F6", "valeur": "PROMOTEUR IMMOBILIER PRIVE"},
    {"code": "F7", "valeur": "INVESTISSEUR PROFESSIONNEL"},
    {"code": "A1", "valeur": "STRUCTURE AGRICOLE"},
    {"code": "A2", "valeur": "STRUCTURE FORESTIERE"},
    {"code": "A3", "valeur": "STRUCTURE DU FONCIER ENVIRONNEMENTALE"},
    {"code": "R1", "valeur": "CONCESSIONNAIRE AUTOROUTIER"},
    {"code": "R2", "valeur": "RESEAU FERRE"},
    {"code": "R3", "valeur": "STRUCTURE AERIENNE"},
    {"code": "R4", "valeur": "STRUCTURE FLUVIALE OU MARITIME"},
    {"code": "R5", "valeur": "RESEAU ELECTRIQUE OU GAZ"},
    {"code": "R0", "valeur": "PROPRIETAIRE DE RESEAU AUTRE"},
    {"code": "M0", "valeur": "AUTRE PERSONNE MORALE"},
    {"code": "X0", "valeur": "PERSONNE PHYSIQUE"},
    {"code": "X1", "valeur": "PERSONNE PHYSIQUE"},
    {"code": "R6", "valeur": "RESEAU EAU OU ASSAINISSEMENT"},
    {"code": "R7", "valeur": "RESEAU DE TELECOMMUNICATION"},
    {"code": "G1", "valeur": "SOCIETE CIVILE IMMOBILIERE"},
    {"code": "G2", "valeur": "PROPRIETE DIVISEE EN LOT"},
    {"code": None, "valeur": "INCONNU"},
]

def etiquette(typo):
    for etiquette, code in TYPES.items():
        if code == typo:
            return etiquette
    return typo

def nom(categorie):
    for elt in CATEGORIES:
        if elt["code"] == categorie:
            return elt["valeur"]
    return categorie


def get_typo_ush():
    df = pd.read_sql_query(
        f"""
SELECT DISTINCT typo_ush FROM result; 
    """,
        con=conn,
    )
    typos = df["typo_ush"].to_list()
    return typos


def get_famille_ols():
    df = pd.read_sql_query(
        f"""
SELECT DISTINCT famille FROM result; 
    """,
        con=conn,
    )
    familles = df["famille"].to_list()
    return familles

def get_perimetre(type_perimetre):
    df = pd.read_sql_query(
        f"""
SELECT DISTINCT perimetre FROM result WHERE type_perimetre='{type_perimetre}'; 
    """,
        con=conn,
    )
    perimetres = df["perimetre"].to_list()
    return perimetres

########################################################################
# FONCTIONS GRAPHIQUES
########################################################################


def achats_ols(type_perimetre, famille):

    resultat = pd.read_sql_query(
        f"""
SELECT typo_ush, 
    perimetre,
    montant_transaction_acheteur
FROM result
WHERE type_perimetre = '{type_perimetre}'
    AND famille = '{famille}';""",
        con=conn,
    )
    titre = "Type de biens achetés par les OLS (période 2010-2020)"
    resultat = resultat.pivot(
        index="perimetre", columns="typo_ush", values="montant_transaction_acheteur"
    )
    resultat = resultat.reset_index()
    fig = px.bar(
        resultat,
        x="perimetre",
        y=resultat.columns,
        color_discrete_sequence=px.colors.qualitative.Alphabet,
        labels={
            "perimetre": "Périmètres",
            "value": "Montant de transactions (M€)",
            "typo_ush": "Typologie",
        },
        title=titre,
    )
    fig.update_layout(
        height=698,
    )
    return fig
    
def proportion_achats_ols(type_perimetre, famille):

    resultat = pd.read_sql_query(
        f"""
    SELECT typo_ush, 
        perimetre,
        montant_transaction_acheteur
    FROM result
    WHERE type_perimetre = '{type_perimetre}'
        AND famille = '{famille}';""",
        con=conn,
    )
    titre = "Proportion des biens achetés par les organismes du logement social (période 2010-2020)"
    resultat = resultat.pivot(
        index="perimetre", columns="typo_ush", values="montant_transaction_acheteur"
    )
    resultat = resultat.reset_index()
    resultat["total"] = resultat.sum(axis=1, numeric_only=True)

    for c in resultat.columns:
        if c not in ("perimetre",):
            resultat[c] = resultat[c] * 100.0 / resultat["total"]

    resultat.drop(columns=["total"], inplace=True)
    fig = px.bar(
        resultat,
        x="perimetre",
        y=resultat.columns,
        color_discrete_sequence=px.colors.qualitative.Alphabet,
        labels={
            "perimetre": "Périmètres",
            "value": "Part du montant total (%)",
            "typo_ush": "Typologie",
        },
        title=titre,
    )
    fig.update_layout(
        height=698,
    )
    return fig

def ventes_ols(type_perimetre, famille):

    resultat = pd.read_sql_query(
        f"""
    SELECT typo_ush, 
        perimetre,
        montant_transaction_vendeur
    FROM result
    WHERE type_perimetre = '{type_perimetre}'
        AND famille = '{famille}';""",
        con=conn,
    )
    titre = "Type de biens vendus par les organismes du logement social (période 2010-2020)"
    resultat = resultat.pivot(
        index="perimetre", columns="typo_ush", values="montant_transaction_vendeur"
    )
    resultat = resultat.reset_index()
    fig = px.bar(
        resultat,
        x="perimetre",
        y=resultat.columns,
        color_discrete_sequence=px.colors.qualitative.Alphabet,
        labels={
            "perimetre": "Périmètres",
            "value": "Montant de transactions (M€)",
            "typo_ush": "Typologie",
        },
        title=titre,
    )
    fig.update_layout(
        height=698,
    )
    return fig


def proportion_ventes_ols(type_perimetre, famille):

    resultat = pd.read_sql_query(
        f"""
    SELECT typo_ush, 
        perimetre,
        montant_transaction_vendeur
    FROM result
    WHERE type_perimetre = '{type_perimetre}'
        AND famille = '{famille}';""",
        con=conn,
    )
    titre = "Proportion de biens vendus par les organismes du logement social selon la région (période 2010-2020)"
    resultat = resultat.pivot(
        index="perimetre", columns="typo_ush", values="montant_transaction_vendeur"
    )
    resultat = resultat.reset_index()
    resultat["total"] = resultat.sum(axis=1, numeric_only=True)

    for c in resultat.columns:
        if c not in ("perimetre",):
            resultat[c] = resultat[c] * 100.0 / resultat["total"]

    resultat.drop(columns=["total"], inplace=True)
    fig = px.bar(
        resultat,
        x="perimetre",
        y=resultat.columns,
        color_discrete_sequence=px.colors.qualitative.Alphabet,
        labels={
            "perimetre": "Périmètres",
            "value": "Part du montant total (%)",
            "typo_ush": "Typologie",
        },
        title=titre,
    )
    fig.update_layout(
        height=698,
    )
    return fig

def montant_achat_vente(perimetre, famille):
    resultat = pd.read_sql_query(
        f"""
    SELECT typo_ush, 
        montant_transaction_vendeur, 
        montant_transaction_acheteur 
    FROM result
    WHERE perimetre = "{perimetre}"
        AND famille = "{famille}"
    ORDER BY (montant_transaction_acheteur - montant_transaction_vendeur) DESC; 
        """,
        con=conn,
    )
    titre = "Montant des transactions impliquant un OLS (période 2010-2020)"
    fig = make_subplots(
        specs=[[{"secondary_y": True}]],
    )
    fig.add_trace(
        go.Bar(
            x=resultat["typo_ush"],
            y=resultat["montant_transaction_vendeur"],
            offsetgroup=1,
            name="Ventes par un OLS (M€)",
            marker_color="rgb(55, 83, 109)",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=resultat["typo_ush"],
            y=resultat["montant_transaction_acheteur"],
            offsetgroup=2,
            name="Achats par un OLS (M€)",
            marker_color="rgb(26, 118, 255)",
        ),
        secondary_y=False,
    )
    fig.update_layout(
        barmode="group", yaxis={"title": "Montant (M€)"}, title=titre, height=698
    )
    return fig

def part_achat_vente(perimetre, famille):
    resultat = pd.read_sql_query(
        f"""
    SELECT typo_ush, 
        proportion_montant_vendeur, 
        proportion_montant_acheteur 
    FROM result
    WHERE perimetre = "{perimetre}"
        AND famille = "{famille}"
    ORDER BY typo_ush; 
        """,
        con=conn,
    )
    titre = "Part du montant des transactions impliquant un OLS par segment de marché (période 2010-2020)"
    fig = make_subplots(
        specs=[[{"secondary_y": True}]],
    )
    fig.add_trace(
        go.Bar(
            x=resultat["typo_ush"],
            y=resultat["proportion_montant_vendeur"],
            offsetgroup=1,
            name="Part des ventes",
            marker_color="rgb(55, 83, 109)",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=resultat["typo_ush"],
            y=resultat["proportion_montant_acheteur"],
            offsetgroup=2,
            name="Part des achats",
            marker_color="rgb(26, 118, 255)",
        ),
        secondary_y=False,
    )
    fig.update_layout(
        barmode="group",
        yaxis={"title": "Pourcentage", "range": [0, 100]},
        title=titre,
        height=698,
    )
    return fig

def transform_sankey(perimetre, famille, typo):
    resultat = pd.read_sql_query(
        f"""
    SELECT codtypprov_ush, 
        codtypproa_ush, 
        montant_transaction 
    FROM flux
    WHERE perimetre = "{perimetre}"
        AND famille = "{famille}"
        AND typo_ush = "{typo}"
        """,
        con=conn,
    )
    categories = list(
        set(resultat["codtypprov_ush"].to_list() + resultat["codtypproa_ush"].to_list())
    )
    source = resultat["codtypprov_ush"].apply(lambda x: categories.index(x)).to_list()
    target = resultat["codtypproa_ush"].apply(lambda x: categories.index(x)).to_list()
    value = (
        resultat["montant_transaction"].apply(lambda x: round(x / 1000000.0)).to_list()
    )
    colors = px.colors.qualitative.Bold
    fig = go.Figure(
        data=[
            go.Sankey(
                orientation="h",
                valueformat=".0f",
                node=dict(
                    pad=35,
                    thickness=25,
                    line=dict(color="black", width=0.5),
                    label=[nom(c) for c in categories],
                    color=[c for c in colors],
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    color=[colors[i] for i in source],
                ),
            )
        ]
    )
    fig.update_layout(
        font=dict(size=12),
        title="Principaux flux de transaction entre acteurs - période 2010-2020",
        height=698,
    )
    return fig

######

## APP

######

st.set_page_config(page_title="Etude USH - Analyse des marchés", page_icon=None,) # layout="wide",)

st.title("Analyse des marchés impliquant les organismes du logement social")
st.subheader("Etude USH - Cerema à partir de DV3F")

famille = st.selectbox("Famille d'OLS", get_famille_ols())

type_perimetre_lbl = st.selectbox("Type de périmètre", TYPES.keys(), index=0)
type_perimetre = TYPES[type_perimetre_lbl]

tab_type_perimetre, tab_perimetre, tab_type_bien = st.tabs(["Type de périmetre", "Périmètre", "Type de biens"])

with tab_type_perimetre:
    st.header(type_perimetre_lbl)
    with st.spinner("Chargement..."):
        st.subheader("Achats par les OLS")
        st.plotly_chart(achats_ols(type_perimetre, famille), use_container_width=True)
        st.plotly_chart(proportion_achats_ols(type_perimetre, famille), use_container_width=True)
        st.subheader("Ventes par les OLS")
        st.plotly_chart(ventes_ols(type_perimetre, famille), use_container_width=True)
        st.plotly_chart(proportion_ventes_ols(type_perimetre, famille), use_container_width=True)
        
with tab_perimetre:
    perimetre = st.selectbox("Périmètre", get_perimetre(type_perimetre), index=0)
    
    st.header(perimetre)
    with st.spinner("Chargement..."):
        st.subheader("Montant Achat - Ventes")
        st.plotly_chart(montant_achat_vente(perimetre, famille), use_container_width=True)
        st.subheader("Proportion Achat - Ventes")
        st.plotly_chart(part_achat_vente(perimetre, famille), use_container_width=True)

with tab_type_bien:
    typo = st.selectbox("Périmètre", get_typo_ush(), index=0)
    st.header(typo + " - " + perimetre)
    with st.spinner("Chargement..."):
        st.subheader("Flux de transaction")
        st.plotly_chart(transform_sankey(perimetre, famille, typo), use_container_width=True)
    