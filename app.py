# -*- coding: utf-8 -*-
"""Artisan DZ Pro \u2014 gestion de devis, chantiers et kredi pour artisans en Alg\u00e9rie.

Lancement :  streamlit run app.py
Aucune d\u00e9pendance exotique : streamlit, pandas, fpdf2.
"""
import os
import sys

import streamlit as st

RACINE = os.path.dirname(os.path.abspath(__file__))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from core import catalog, db  # noqa: E402
from core.fmt import dz  # noqa: E402
from ui import compat  # noqa: E402
from ui import components as c  # noqa: E402
from ui import theme  # noqa: E402
from ui.views import (accueil, calculs, chantiers, clients, devis,  # noqa: E402
                                  devis_express, kredi, prix, reglages)

# Meme code sur PC (Streamlit 1.4x) et en ligne sur Streamlit Cloud (1.6x+).
compat.activer()

PAGES = [
    ("devis_express", "Devis", "\u26a1", devis_express.afficher),
    ("accueil", "\u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629", "\U0001f3e0", accueil.afficher),
    ("devis", "\u0627\u0644\u0623\u0631\u0634\u064a\u0641", "\U0001f4c4", devis.afficher),
    ("chantiers", "\u0627\u0644\u0648\u0631\u0634\u0627\u062a", "\U0001f3d7\ufe0f", chantiers.afficher),
    ("kredi", "\u0627\u0644\u0643\u0631\u064a\u062f\u064a", "\U0001f4b0", kredi.afficher),
    ("clients", "\u0627\u0644\u0632\u0628\u0627\u0626\u0646", "\U0001f465", clients.afficher),
    ("calculs", "\u0627\u0644\u062d\u0627\u0633\u0628\u0629", "\U0001f9ee", calculs.afficher),
    ("prix", "\u0627\u0644\u0623\u0633\u0639\u0627\u0631", "\U0001f4da", prix.afficher),
    ("reglages", "\u0627\u0644\u0625\u0639\u062f\u0627\u062f\u0627\u062a", "\u2699\ufe0f", reglages.afficher),
]
PRINCIPALES = ["devis_express", "accueil", "devis", "kredi", "clients"]


def configurer():
    st.set_page_config(page_title="Artisan DZ Pro", page_icon="\U0001f9f0",
                       layout="centered", initial_sidebar_state="collapsed")
    theme.appliquer()
    db.init()
    st.session_state.setdefault("page", "devis_express")


def bienvenue():
    """Onboarding : 3 champs au premier lancement, jamais un formulaire de 20 lignes."""
    st.markdown('<div class="hero"><div class="lbl">\u0645\u0631\u062d\u0628\u0627 \u0628\u0643 (Bienvenue)</div>'
                '<div class="val">Artisan DZ Pro</div>'
                '<div class="hero-sub">\u0639\u0631\u0648\u0636 \u0627\u0644\u0623\u0633\u0639\u0627\u0631\u060c \u0627\u0644\u0648\u0631\u0634\u0627\u062a \u0648\u0627\u0644\u0643\u0631\u064a\u062f\u064a '
                '\u2014 \u0628\u0627\u0644\u062f\u064a\u0646\u0627\u0631\u060c \u0628\u0644\u0627 TVA\u060c \u0628\u0644\u0627 \u0645\u062d\u0627\u0633\u0628\u0629 \u0645\u0639\u0642\u062f\u0629.'
                '<br>Devis, chantiers et kredi \u2014 en dinars, sans TVA, sans compta compliqu\u00e9e.</div></div>',
                unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="sec" style="margin-top:0">'
                    '\u0663 \u0645\u0639\u0644\u0648\u0645\u0627\u062a \u0648\u062a\u0628\u062f\u0623 (3 informations et c\'est parti)</div>',
                    unsafe_allow_html=True)
        nom = st.text_input("\u0627\u0633\u0645 \u0627\u0644\u0645\u0624\u0633\u0633\u0629 \u0623\u0648 \u0627\u0633\u0645\u0643 (Nom)", key="ob_nom",
                            placeholder="Ets. Ma\u00efz \u2014 Peinture")
        type_compte = st.radio(c.bi("\u0646\u0648\u0639 \u0627\u0644\u062d\u0633\u0627\u0628", "Type de compte"),
                               [c.bi("\u0635\u0627\u062d\u0628 \u0635\u0646\u0639\u0629", "Artisan"),
                                c.bi("\u0645\u0642\u0627\u0648\u0644", "Entrepreneur")],
                               horizontal=True, key="ob_type")
        col1, col2 = st.columns(2)
        if type_compte.endswith("(Artisan)"):
            metier = col1.selectbox("\u0645\u0647\u0646\u062a\u0643 (M\u00e9tier)",
                                    ["Peintre", "Ma\u00e7on", "Plombier", "\u00c9lectricien",
                                     "Pl\u00e2trier", "Carreleur", "Multi-services"], key="ob_metier")
        else:
            metier = "Multi-services"
            col1.markdown('<div class="sm muted" style="padding-top:26px">'
                          + c.bi("\u0627\u0644\u0645\u0642\u0627\u0648\u0644 \u064a\u0631\u0649 \u0643\u0644 \u0627\u0644\u0645\u064a\u0627\u062f\u064a\u0646 \u0648\u0627\u0644\u0646\u0645\u0627\u0630\u062c",
                                 "Le compte Entrepreneur voit tous les m\u00e9tiers.")
                          + "</div>", unsafe_allow_html=True)
        tel = col2.text_input("\u0631\u0642\u0645 \u0627\u0644\u0647\u0627\u062a\u0641 (T\u00e9l\u00e9phone)", key="ob_tel",
                              placeholder="0555 12 34 56")
        if st.button("\u0627\u0628\u062f\u0623 (Commencer)", type="primary", use_container_width=True,
                     disabled=not nom.strip()):
            db.set_param("entreprise_nom", nom.strip())
            db.set_param("entreprise_metier", metier)
            db.set_param("entreprise_tel", tel.strip())
            db.set_param("type_compte",
                         "artisan" if type_compte.endswith("(Artisan)") else "entrepreneur")
            insere = catalog.ensemencer(catalog.metiers_artisan() or None)
            db.set_param("onboarding_fait", "1")
            c.toast(c.bi("\u0645\u0643\u062a\u0628\u0629 \u0627\u0644\u0623\u0633\u0639\u0627\u0631 \u062c\u0627\u0647\u0632\u0629: %d \u062e\u062f\u0645\u0629",
                         "Biblioth\u00e8que pr\u00eate : %d prestations", insere))
            st.rerun()
        st.caption("\u0643\u0644\u0634 \u064a\u0628\u0642\u0649 \u0641\u064a \u062c\u0647\u0627\u0632\u0643\u060c \u0641\u064a \u0645\u0644\u0641 \u0628\u0633\u064a\u0637 artisan.db "
                   "(Tout reste sur votre appareil).")


def navigation():
    """Barre d'onglets fixe en bas : 5 destinations, pouce accessible."""
    with st.container(key="navbar"):
        colonnes = st.columns(len(PRINCIPALES) + 1)
        for i, cle in enumerate(PRINCIPALES):
            page = [p for p in PAGES if p[0] == cle][0]
            actif = st.session_state["page"] == cle
            if colonnes[i].button("%s\n%s" % (page[2], page[1]), key="nav_%s" % cle,
                                  use_container_width=True,
                                  type="primary" if actif else "secondary"):
                aller(cle)
        if colonnes[-1].button("\u22ef\n\u0627\u0644\u0645\u0632\u064a\u062f", key="nav_plus", use_container_width=True,
                               type="primary" if st.session_state["page"] in
                               ("calculs", "reglages", "chantiers", "prix")
                               else "secondary"):
            st.session_state["menu_plus"] = True
    if st.session_state.get("menu_plus"):
        _menu_plus()


@c.dialogue("\u0627\u0644\u0645\u0632\u064a\u062f (Plus)")
def _menu_plus():
    for cle, libelle, icone, _ in PAGES:
        if cle in PRINCIPALES:
            continue
        if st.button("%s  %s" % (icone, libelle), key="plus_%s" % cle, use_container_width=True):
            st.session_state["menu_plus"] = False
            aller(cle)
    if st.button("Fermer", use_container_width=True):
        st.session_state["menu_plus"] = False
        st.rerun()


def aller(cle):
    st.session_state["page"] = cle
    st.session_state.pop("doc_ouvert", None)
    st.session_state.pop("chantier_ouvert", None)
    st.rerun()


def main():
    configurer()
    if db.get_param("onboarding_fait") != "1":
        bienvenue()
        return
    page = st.session_state.get("page", "devis_express")
    rendu = dict((p[0], p[3]) for p in PAGES).get(page, devis_express.afficher)
    rendu()
    navigation()


if __name__ == "__main__":
    main()
else:
    main()
