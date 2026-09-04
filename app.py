# -*- coding: utf-8 -*-
"""Artisan DZ Pro — devis, chantiers, kredi et annuaire pour artisans en Algérie.

Lancement :  streamlit run streamlit_app.py   (ou  streamlit run app.py)
Dépendances : streamlit, pandas, fpdf2. Rien d'exotique.

Architecture :
    app.py            → configuration, onboarding, démarrage
    ui/routes.py      → pages (st.Page / st.navigation) + onglets hauts
    ui/champs.py      → libellés bilingues verticaux (arabe gras / français gris)
    ui/cartes.py      → listings en cartes CSS + actions Appeler/WhatsApp/BaridiMob
    ui/etat.py        → mémoire d'écran (filtres, fiche ouverte)
    ui/theme.py       → CSS (Cairo + Inter)
    core/*            → données, métier, PDF, wilayas
"""
import os
import sys

import streamlit as st

RACINE = os.path.dirname(os.path.abspath(__file__))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from core import catalog, db  # noqa: E402
from ui import champs, compat, routes, theme  # noqa: E402
from ui import components as c  # noqa: E402

# Meme code sur PC (Streamlit 1.4x) et en ligne sur Streamlit Cloud (1.6x+).
compat.activer()

DEFAUT = "devis_express"


def configurer():
    st.set_page_config(
        page_title="Artisan DZ Pro", page_icon="\U0001f9f0", layout="centered",
        initial_sidebar_state="collapsed")   # v14 : plus de menu lateral
    theme.appliquer()
    db.init()
    st.session_state.setdefault("page", DEFAUT)


def bienvenue():
    """Onboarding : 4 champs au premier lancement, jamais un formulaire de 20 lignes."""
    st.markdown('<div class="hero"><div class="lbl">\u0645\u0631\u062d\u0628\u0627 \u0628\u0643 \u00b7 Bienvenue</div>'
                '<div class="val">Artisan DZ Pro</div>'
                '<div class="hero-sub">\u0639\u0631\u0648\u0636 \u0627\u0644\u0623\u0633\u0639\u0627\u0631\u060c \u0627\u0644\u0648\u0631\u0634\u0627\u062a \u0648\u0627\u0644\u0643\u0631\u064a\u062f\u064a '
                '\u2014 \u0628\u0627\u0644\u062f\u064a\u0646\u0627\u0631\u060c \u0628\u0644\u0627 TVA\u060c \u0628\u0644\u0627 \u0645\u062d\u0627\u0633\u0628\u0629 \u0645\u0639\u0642\u062f\u0629.'
                '<br>Devis, chantiers et kredi \u2014 en dinars, sans TVA, sans compta compliqu\u00e9e.</div></div>',
                unsafe_allow_html=True)
    with st.container(border=True):
        champs.bloc_titre("\u0663 \u0645\u0639\u0644\u0648\u0645\u0627\u062a \u0648\u062a\u0628\u062f\u0623",
                          "3 informations et c'est parti", "\U0001f680")
        nom = champs.texte("\u0627\u0633\u0645 \u0627\u0644\u0645\u0624\u0633\u0633\u0629 \u0623\u0648 \u0627\u0633\u0645\u0643",
                           "Nom de l'entreprise ou votre nom", requis=True,
                           icone="\U0001f3f7\ufe0f", key="ob_nom",
                           placeholder="Ets. Ma\u00efz \u2014 Peinture")
        type_compte = champs.radio("\u0646\u0648\u0639 \u0627\u0644\u062d\u0633\u0627\u0628", "Type de compte",
                                   ["\u0635\u0627\u062d\u0628 \u0635\u0646\u0639\u0629 \u00b7 Artisan",
                                    "\u0645\u0642\u0627\u0648\u0644 \u00b7 Entrepreneur"],
                                   icone="\U0001f464", key="ob_type")
        artisan = str(type_compte or "").endswith("Artisan")

        col1, col2 = st.columns(2)
        with col1:
            if artisan:
                metier = champs.choix("\u0645\u0647\u0646\u062a\u0643", "Votre m\u00e9tier",
                                      ["Peintre", "Ma\u00e7on", "Plombier", "\u00c9lectricien",
                                       "Pl\u00e2trier", "Carreleur", "Multi-services"],
                                      icone="\U0001f6e0\ufe0f", key="ob_metier")
            else:
                metier = "Multi-services"
                champs.label("\u0643\u0644 \u0627\u0644\u0645\u064a\u0627\u062f\u064a\u0646", "Tous les m\u00e9tiers", icone="\U0001f4d0")
                st.caption("Le compte Entrepreneur voit tous les m\u00e9tiers et tous les mod\u00e8les.")
        with col2:
            tel = champs.texte("\u0631\u0642\u0645 \u0627\u0644\u0647\u0627\u062a\u0641", "T\u00e9l\u00e9phone",
                               icone="\U0001f4f1", key="ob_tel", placeholder="0555 12 34 56")
        wilaya = champs.wilaya(key="ob_wilaya")

        if st.button("\u0627\u0628\u062f\u0623 \u00b7 Commencer", type="primary",
                     use_container_width=True, disabled=not (nom or "").strip()):
            db.set_param("entreprise_nom", (nom or "").strip())
            db.set_param("entreprise_metier", metier)
            db.set_param("entreprise_tel", (tel or "").strip())
            db.set_param("entreprise_wilaya", str(wilaya or ""))
            db.set_param("type_compte", "artisan" if artisan else "entrepreneur")
            insere = catalog.ensemencer(catalog.metiers_artisan() or None)
            db.set_param("onboarding_fait", "1")
            c.toast(c.bi("\u0645\u0643\u062a\u0628\u0629 \u0627\u0644\u0623\u0633\u0639\u0627\u0631 \u062c\u0627\u0647\u0632\u0629: %d \u062e\u062f\u0645\u0629",
                         "Biblioth\u00e8que pr\u00eate : %d prestations", insere))
            st.rerun()
        st.caption("\u0643\u0644\u0634 \u064a\u0628\u0642\u0649 \u0641\u064a \u062c\u0647\u0627\u0632\u0643\u060c \u0641\u064a \u0645\u0644\u0641 \u0628\u0633\u064a\u0637 artisan.db "
                   "(Tout reste sur votre appareil).")


def main():
    configurer()
    if db.get_param("onboarding_fait") != "1":
        bienvenue()
        return
    if routes.moderne():
        routes.executer(db.get_param("entreprise_nom") or "", DEFAUT)
    else:
        routes.executer_repli(db.get_param("entreprise_nom") or "", DEFAUT)


# Streamlit relance CE script a chaque interaction : main() doit donc etre
# appele a chaque execution, et jamais depuis un simple import (un module
# importe n'est charge qu'une seule fois -> ecran blanc aux executions
# suivantes en ligne).
if __name__ == "__main__":
    main()
