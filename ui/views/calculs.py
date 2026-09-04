# -*- coding: utf-8 -*-
"""Calculateurs m\u00e9tier : m\u00e8tr\u00e9 rapide, r\u00e9sultat chiffr\u00e9 et envoi direct vers un devis."""
import math
import uuid

import streamlit as st

from core import catalog, docs
from core.fmt import dz, nombre
from .. import components as c
from . import _communs as k


def afficher():
    c.entete(c.bi("\u0627\u0644\u062d\u0627\u0633\u0628\u0629", "Calculateurs"),
             c.bi("\u0645\u062a\u0631\u0627\u062c\u0639\u0629 \u0633\u0631\u064a\u0639\u0629 \u0641\u064a \u0627\u0644\u0648\u0631\u0634\u0629", "M\u00e9tr\u00e9 rapide"))
    onglets = st.tabs(["\U0001f9f1 Carrelage", "\U0001f3a8 Peinture", "\U0001f9f1 Ma\u00e7onnerie",
                       "\U0001fea3 B\u00e9ton", "\U0001f3d7\ufe0f Pl\u00e2tre & chape"])
    with onglets[0]:
        _carrelage()
    with onglets[1]:
        _peinture()
    with onglets[2]:
        _maconnerie()
    with onglets[3]:
        _beton()
    with onglets[4]:
        _platre()


# --------------------------------------------------------------------------
def _surface(prefixe, defaut_l=4.0, defaut_L=5.0):
    mode = c.pilules_filtre("Saisie", ["Longueur \u00d7 largeur", "Surface directe"],
                            prefixe + "_mode", "Longueur \u00d7 largeur")
    if mode == "Surface directe":
        return st.number_input("Surface (m2)", min_value=0.0, value=defaut_l * defaut_L, step=1.0,
                               key=prefixe + "_s")
    col1, col2 = st.columns(2)
    longueur = col1.number_input("Longueur (m)", min_value=0.0, value=defaut_L, step=0.5,
                                 key=prefixe + "_L")
    largeur = col2.number_input("Largeur (m)", min_value=0.0, value=defaut_l, step=0.5,
                                key=prefixe + "_l")
    st.caption("Surface : %s m2" % nombre(longueur * largeur))
    return longueur * largeur


def _resultats(titre, lignes):
    with st.container(border=True):
        st.markdown('<div class="sec" style="margin-top:0">%s</div>' % c.e(titre),
                    unsafe_allow_html=True)
        for libelle, valeur in lignes:
            c.ligne_stat(libelle, valeur)


def _vers_devis(prefixe, description, unite, quantite, prix_defaut):
    with st.container(border=True):
        st.markdown('<div class="sec" style="margin-top:0">Transformer en poste de devis</div>',
                    unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        prix = col1.number_input("Prix / %s" % unite, min_value=0.0, value=float(prix_defaut),
                                 step=50.0, key=prefixe + "_prix")
        col2.markdown('<div class="money" style="font-size:20px;padding-top:22px;text-align:right">%s'
                      '</div>' % dz(quantite * prix), unsafe_allow_html=True)
        if st.button("\uff0b Ajouter \u00e0 un devis", key=prefixe + "_add", use_container_width=True,
                     type="primary"):
            st.session_state[prefixe + "_dlg"] = True
        if st.session_state.get(prefixe + "_dlg"):
            _dialog_vers_devis(prefixe, description, unite, quantite, prix)


@c.dialogue("Ajouter au devis")
def _dialog_vers_devis(prefixe, description, unite, quantite, prix):
    ligne = catalog.ligne_vide(description, unite, round(quantite, 2), prix)
    st.markdown('<div class="msg">%s \u2014 %s %s \u00d7 %s = <b>%s</b></div>'
                % (c.e(description), nombre(quantite), c.e(unite), nombre(prix),
                   dz(quantite * prix)), unsafe_allow_html=True)
    ouverts = docs.documents(type_doc="Devis", limite=20)
    choix = ["\uff0b Nouveau devis"] + ["%s \u00b7 %s" % (d["numero"], d.get("client") or "")
                                        for d in ouverts]
    selection = st.selectbox("Destination", choix, key=prefixe + "_dest")
    client_id = None
    if selection == "\uff0b Nouveau devis":
        client_id = k.selecteur_client("Client", prefixe + "_cli")
    if st.button("Valider", type="primary", use_container_width=True, key=prefixe + "_ok"):
        if selection == "\uff0b Nouveau devis":
            doc_id = docs.creer_document(client_id, None, "Devis", [ligne])
        else:
            doc_id = ouverts[choix.index(selection) - 1]["id"]
            existantes = docs.charger_lignes(doc_id)
            docs.remplacer_lignes(doc_id, [dict(x) for x in existantes] + [ligne])
        st.session_state[prefixe + "_dlg"] = False
        c.toast("Poste ajout\u00e9 au devis")
        k.ouvrir_document(doc_id)
    if st.button("Fermer", use_container_width=True, key=prefixe + "_close"):
        st.session_state[prefixe + "_dlg"] = False
        st.rerun()


# --------------------------------------------------------------------------
def _carrelage():
    surface = _surface("carr")
    col1, col2 = st.columns(2)
    perte = col1.slider("Perte / coupe (%)", 0, 20, 10, key="carr_perte")
    format_carreau = col2.selectbox("Format", ["30\u00d730", "40\u00d740", "45\u00d745", "60\u00d760"],
                                    key="carr_fmt")
    cote = {"30\u00d730": 0.30, "40\u00d740": 0.40, "45\u00d745": 0.45, "60\u00d760": 0.60}[format_carreau]

    surface_totale = surface * (1 + perte / 100.0)
    carreaux = math.ceil(surface_totale / (cote * cote)) if cote else 0
    colle_kg = surface_totale * 5
    sacs_colle = math.ceil(colle_kg / 25) if colle_kg else 0
    joint_kg = surface_totale * 0.5

    _resultats("Besoins estim\u00e9s", [
        ("Surface \u00e0 poser (perte incluse)", "%s m2" % nombre(surface_totale)),
        ("Carreaux %s" % format_carreau, "%d U" % carreaux),
        ("Colle (5 kg/m2)", "%s kg \u00b7 %d sacs de 25 kg" % (nombre(colle_kg), sacs_colle)),
        ("Joint", "%s kg" % nombre(joint_kg)),
    ])
    _vers_devis("carr", "Pose de carrelage %s" % format_carreau, "m2", surface, 1200)


def _peinture():
    surface = _surface("pein")
    col1, col2, col3 = st.columns(3)
    couches = col1.number_input("Couches", min_value=1, max_value=4, value=2, key="pein_c")
    rendement = col2.number_input("Rendement (m2/L)", min_value=1.0, value=10.0, step=1.0,
                                  key="pein_r")
    enduit = col3.checkbox("Enduit", value=True, key="pein_e")

    litres = surface * couches / rendement if rendement else 0
    bidons = math.ceil(litres / 20) if litres else 0
    enduit_kg = surface * 1.0 if enduit else 0

    _resultats("Besoins estim\u00e9s", [
        ("Peinture", "%s L \u00b7 %d bidon(s) de 20 L" % (nombre(litres), bidons)),
        ("Enduit de lissage", "%s kg" % nombre(enduit_kg)),
        ("Surface trait\u00e9e", "%s m2 \u00d7 %d couche(s)" % (nombre(surface), couches)),
    ])
    _vers_devis("pein", "Peinture %d couches" % couches, "m2", surface, 550)


def _maconnerie():
    surface = _surface("mac", 3.0, 8.0)
    materiau = c.pilules_filtre("Mat\u00e9riau", ["Parpaing 20", "Brique 8 trous", "Brique 12 trous"],
                                "mac_mat", "Parpaing 20")
    par_m2 = {"Parpaing 20": 12.5, "Brique 8 trous": 23.0, "Brique 12 trous": 16.0}[materiau]
    unites = math.ceil(surface * par_m2 * 1.05)
    sacs = math.ceil(surface * 0.5)
    sable = surface * 0.04

    _resultats("Besoins estim\u00e9s", [
        (materiau + " (+5 %% de casse)", "%d U" % unites),
        ("Ciment", "%d sac(s) de 50 kg" % sacs),
        ("Sable", "%s m3" % nombre(sable)),
    ])
    _vers_devis("mac", "Ma\u00e7onnerie %s" % materiau.lower(), "m2", surface, 1800)


def _beton():
    col1, col2, col3 = st.columns(3)
    longueur = col1.number_input("Longueur (m)", min_value=0.0, value=5.0, step=0.5, key="bet_L")
    largeur = col2.number_input("Largeur (m)", min_value=0.0, value=4.0, step=0.5, key="bet_l")
    epaisseur = col3.number_input("\u00c9paisseur (cm)", min_value=1.0, value=10.0, step=1.0,
                                  key="bet_e")
    dosage = c.pilules_filtre("Dosage ciment", ["350 kg/m3", "300 kg/m3", "250 kg/m3"],
                              "bet_dos", "350 kg/m3")
    kg = int(dosage.split()[0])

    volume = longueur * largeur * epaisseur / 100.0
    ciment_kg = volume * kg
    sacs = math.ceil(ciment_kg / 50) if ciment_kg else 0

    _resultats("Besoins estim\u00e9s", [
        ("Volume de b\u00e9ton", "%s m3" % nombre(volume)),
        ("Ciment", "%s kg \u00b7 %d sac(s) de 50 kg" % (nombre(ciment_kg), sacs)),
        ("Sable", "%s m3" % nombre(volume * 0.4)),
        ("Gravier", "%s m3" % nombre(volume * 0.8)),
        ("Eau", "%s L" % nombre(volume * 175)),
    ])
    _vers_devis("bet", "Coulage b\u00e9ton dos\u00e9 \u00e0 %d kg/m3" % kg, "m3", volume, 22000)


def _platre():
    choix = c.pilules_filtre("Type", ["Pl\u00e2tre mural", "Chape"], "plt_type", "Pl\u00e2tre mural")
    surface = _surface("plt", 2.8, 10.0)
    if choix == "Pl\u00e2tre mural":
        epaisseur = st.slider("\u00c9paisseur (mm)", 5, 30, 12, key="plt_ep")
        kg = surface * 0.9 * epaisseur
        sacs = math.ceil(kg / 40) if kg else 0
        _resultats("Besoins estim\u00e9s", [
            ("Pl\u00e2tre", "%s kg \u00b7 %d sac(s) de 40 kg" % (nombre(kg), sacs)),
            ("Surface", "%s m2 \u00b7 %d mm" % (nombre(surface), epaisseur)),
        ])
        _vers_devis("plt", "Enduit pl\u00e2tre %d mm" % epaisseur, "m2", surface, 700)
    else:
        epaisseur = st.slider("\u00c9paisseur (cm)", 2, 10, 5, key="chp_ep")
        volume = surface * epaisseur / 100.0
        ciment_kg = volume * 350
        sacs = math.ceil(ciment_kg / 50) if ciment_kg else 0
        _resultats("Besoins estim\u00e9s", [
            ("Volume de chape", "%s m3" % nombre(volume)),
            ("Ciment (dosage 350)", "%s kg \u00b7 %d sac(s)" % (nombre(ciment_kg), sacs)),
            ("Sable", "%s m3" % nombre(volume * 1.1)),
        ])
        _vers_devis("chp", "Chape ciment %d cm" % epaisseur, "m2", surface, 900)
