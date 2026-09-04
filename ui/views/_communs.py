# -*- coding: utf-8 -*-
"""Briques partag\u00e9es entre les \u00e9crans : s\u00e9lecteurs, cr\u00e9ations rapides, navigation."""
from datetime import date

import streamlit as st

from core import db
from core.fmt import dz
from core.metier import MODES_PAIEMENT, TYPES_TRAVAUX
from .. import components as c


# ------------------------------------------------------------------ navigation
def aller(page, **etat):
    """Changement de page, compatible navigation multipage (st.Page) et repli."""
    cle_page = str(page).strip().lower()
    st.session_state["page"] = cle_page
    for cle, valeur in etat.items():
        st.session_state[cle] = valeur
    try:
        from ui import routes                      # import tardif : evite un cycle
        if routes.moderne() and hasattr(st, "switch_page"):
            _sections, pages = routes.construire()
            if cle_page in pages:
                st.switch_page(pages[cle_page])
                return
    except Exception:
        pass
    st.rerun()


def ouvrir_document(doc_id):
    st.session_state["doc_ouvert"] = doc_id
    st.session_state.pop("lignes_edition", None)
    st.session_state.pop("doc_lignes_id", None)
    aller("Devis")


def ouvrir_chantier(chantier_id):
    st.session_state["chantier_ouvert"] = chantier_id
    aller("Chantiers")


# ------------------------------------------------------------------ listes
def clients():
    return db.q("SELECT * FROM clients ORDER BY nom")


def chantiers(actifs_seulement=False):
    sql = ("SELECT ch.*, c.nom AS client FROM chantiers ch "
           "LEFT JOIN clients c ON c.id = ch.client_id")
    if actifs_seulement:
        sql += " WHERE ch.statut='En cours'"
    return db.q(sql + " ORDER BY ch.id DESC")


def selection_differee(cle):
    """\u00c0 appeler AVANT le widget : r\u00e9cup\u00e8re une s\u00e9lection diff\u00e9r\u00e9e (cl\u00e9 pre_<cle>)
    et r\u00e9initialise l'\u00e9tat du widget pour qu'elle devienne la valeur affich\u00e9e.
    \u00c9vite l'erreur Streamlit 'cannot be modified after the widget is instantiated'."""
    valeur = st.session_state.pop("pre_" + cle, None)
    if valeur is not None:
        st.session_state.pop(cle, None)
    return valeur


def selecteur_client(label="Client", cle="sel_client", valeur=None, autoriser_vide=True):
    liste = clients()
    options = ([None] if autoriser_vide else []) + [x["id"] for x in liste]
    noms = {x["id"]: x["nom"] for x in liste}
    index = options.index(valeur) if valeur in options else 0
    numeros = {identifiant: "[%02d] %s" % (i + 1, noms[identifiant])
               for i, identifiant in enumerate(x["id"] for x in liste)}
    return st.selectbox(label, options, index=index, key=cle,
                        format_func=lambda i: numeros.get(
                            i, "\u2014 Choisir un client \u2014"))


def selecteur_chantier(label="Chantier", cle="sel_chantier", valeur=None, client_id=None):
    liste = chantiers()
    if client_id:
        prioritaires = [x for x in liste if x["client_id"] == client_id]
        liste = prioritaires + [x for x in liste if x["client_id"] != client_id]
    options = [None] + [x["id"] for x in liste]
    noms = {x["id"]: x["nom"] for x in liste}
    index = options.index(valeur) if valeur in options else 0
    return st.selectbox(label, options, index=index, key=cle,
                        format_func=lambda i: noms.get(i, "\u2014 Aucun chantier \u2014"))


# ------------------------------------------------------------------ creations rapides
def formulaire_client_rapide(prefixe="rapide"):
    """Cr\u00e9ation d'un client : nom, t\u00e9l\u00e9phone, wilaya. Retourne l'id ou None.

    Libell\u00e9s bilingues verticaux (arabe gras au-dessus, fran\u00e7ais gris dessous).
    """
    from ui import champs

    nom = champs.texte("\u0627\u0633\u0645 \u0627\u0644\u0632\u0628\u0648\u0646", "Nom du client", requis=True,
                       icone="\U0001f464", key=prefixe + "_nom",
                       placeholder="Mme Kadri, Si Ahmed\u2026")
    col1, col2 = st.columns(2)
    with col1:
        tel = champs.texte("\u0627\u0644\u0647\u0627\u062a\u0641", "T\u00e9l\u00e9phone", icone="\U0001f4f1",
                           key=prefixe + "_tel", placeholder="0661 22 33 44")
    with col2:
        ville = champs.texte("\u0627\u0644\u0628\u0644\u062f\u064a\u0629", "Commune / Ville",
                             key=prefixe + "_ville", placeholder="Bab Ezzouar")
    wilaya = champs.wilaya(key=prefixe + "_wilaya")
    if st.button("\U0001f4be \u062d\u0641\u0637 \u00b7 Enregistrer le client", type="primary",
                 use_container_width=True, key=prefixe + "_ok",
                 disabled=not (nom or "").strip()):
        client_id = db.run(
            "INSERT INTO clients (nom,telephone,ville,wilaya,date_creation) "
            "VALUES (?,?,?,?,?)",
            (nom.strip(), (tel or "").strip(), (ville or "").strip(), wilaya,
             date.today().isoformat()))
        c.toast("Client %s ajout\u00e9" % nom.strip())
        return client_id
    return None


def formulaire_chantier_rapide(client_id=None, prefixe="chrapide"):
    nom = st.text_input("Nom du chantier *", key=prefixe + "_nom",
                        placeholder="Villa Dar El Be\u00efda \u2014 Peinture")
    col1, col2 = st.columns(2)
    type_travaux = col1.selectbox("Type de travaux", TYPES_TRAVAUX, key=prefixe + "_type")
    adresse = col2.text_input("Adresse", key=prefixe + "_adr", placeholder="Cit\u00e9 \u2026, Alger")
    if st.button("Cr\u00e9er le chantier", type="primary", use_container_width=True,
                 key=prefixe + "_ok", disabled=not nom.strip()):
        chantier_id = db.run(
            "INSERT INTO chantiers (nom,client_id,adresse,type_travaux,statut,date_debut) "
            "VALUES (?,?,?,?,?,?)",
            (nom.strip(), client_id, adresse.strip(), type_travaux, "En cours", date.today().isoformat()))
        c.toast("Chantier cr\u00e9\u00e9")
        return chantier_id
    return None


# ------------------------------------------------------------------ saisie argent
def champ_montant(label, cle, valeur=0.0, aide=None, pas=500.0):
    return st.number_input(label, min_value=0.0, value=float(valeur), step=pas,
                           format="%.0f", key=cle, help=aide)


def boutons_montants_rapides(cle, montants=(1000, 2000, 5000, 10000)):
    """Raccourcis de saisie : un tap suffit sur le chantier."""
    colonnes = st.columns(len(montants))
    for col, montant in zip(colonnes, montants):
        if col.button(dz(montant, False), key="%s_%d" % (cle, montant), use_container_width=True):
            st.session_state[cle] = float(montant)
            st.rerun()


def selecteur_mode_paiement(cle="mode_paiement"):
    return c.pilules_filtre("Mode", MODES_PAIEMENT, cle, MODES_PAIEMENT[0])
