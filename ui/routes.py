# -*- coding: utf-8 -*-
"""Architecture mobile-first : st.Page + st.navigation, navigation en haut.

v14 : la barre laterale est abandonnee. La navigation devient une barre
d'application collante (marque + page courante) suivie d'une rangee d'onglets
ronds defilables horizontalement, dessinee en UN seul rendu HTML (des liens,
pas des widgets : aucun rerun pour changer d'ecran).

Trois niveaux de repli, du plus moderne au plus ancien :
  1. st.navigation(..., position="hidden") + nos onglets hauts  (Streamlit recent)
  2. st.navigation(...) avec le menu natif laisse visible       (Streamlit 1.31+)
  3. aiguillage par session_state + rangee de boutons           (sans st.Page)
"""
import streamlit as st

from ui import components as c
from ui import theme
from ui.views import (accueil, annuaire, calculs, chantiers, clients, devis,
                      devis_express, kredi, prix, reglages)

# groupe, cle, fonction, titre affiche, icone, url
DEFINITIONS = [
    ("atelier", "devis_express", devis_express.afficher,
     "\u062f\u0631\u0627\u0633\u0629 \u0633\u0639\u0631 \u00b7 Devis express", "\u26a1", "devis-express"),
    ("atelier", "accueil", accueil.afficher,
     "\u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629 \u00b7 Accueil", "\U0001f3e0", "accueil"),
    ("atelier", "devis", devis.afficher,
     "\u0627\u0644\u0623\u0631\u0634\u064a\u0641 \u00b7 Devis & factures", "\U0001f4c4", "archives"),
    ("atelier", "chantiers", chantiers.afficher,
     "\u0627\u0644\u0648\u0631\u0634\u0627\u062a \u00b7 Chantiers", "\U0001f3d7\ufe0f", "chantiers"),
    ("reseau", "annuaire", annuaire.afficher,
     "\u0627\u0644\u062d\u0631\u0641\u064a\u0648\u0646 \u00b7 Annuaire", "\U0001f465", "annuaire"),
    ("reseau", "clients", clients.afficher,
     "\u0627\u0644\u0632\u0628\u0627\u0626\u0646 \u00b7 Clients", "\U0001f91d", "clients"),
    ("argent", "kredi", kredi.afficher,
     "\u0627\u0644\u0643\u0631\u064a\u062f\u064a \u00b7 Cr\u00e9ances", "\U0001f4b0", "kredi"),
    ("outils", "calculs", calculs.afficher,
     "\u0627\u0644\u062d\u0627\u0633\u0628\u0629 \u00b7 Calculateur", "\U0001f9ee", "calculs"),
    ("outils", "prix", prix.afficher,
     "\u0627\u0644\u0623\u0633\u0639\u0627\u0631 \u00b7 Biblioth\u00e8que", "\U0001f4da", "prix"),
    ("outils", "reglages", reglages.afficher,
     "\u0627\u0644\u0625\u0639\u062f\u0627\u062f\u0627\u062a \u00b7 R\u00e9glages", "\u2699\ufe0f", "reglages"),
]

GROUPES = [
    ("atelier", "\u0627\u0644\u0648\u0631\u0634\u0629 \u00b7 Atelier"),
    ("reseau", "\u0627\u0644\u0634\u0628\u0643\u0629 \u00b7 R\u00e9seau"),
    ("argent", "\u0627\u0644\u0645\u0627\u0644 \u00b7 Argent"),
    ("outils", "\u0623\u062f\u0648\u0627\u062a \u00b7 Outils"),
]

# Onglets hauts : icone + libelle arabe court (le titre complet reste en
# infobulle). L'ordre suit DEFINITIONS, la rangee defile au doigt.
PILULES = {
    "devis_express": ("\u26a1", "\u062f\u0631\u0627\u0633\u0629 \u0633\u0639\u0631", "Devis"),
    "accueil": ("\U0001f3e0", "\u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629", "Accueil"),
    "devis": ("\U0001f4c4", "\u0627\u0644\u0623\u0631\u0634\u064a\u0641", "Archives"),
    "chantiers": ("\U0001f3d7\ufe0f", "\u0627\u0644\u0648\u0631\u0634\u0627\u062a", "Chantiers"),
    "annuaire": ("\U0001f465", "\u0627\u0644\u062d\u0631\u0641\u064a\u0648\u0646", "Artisans"),
    "clients": ("\U0001f91d", "\u0627\u0644\u0632\u0628\u0627\u0626\u0646", "Clients"),
    "kredi": ("\U0001f4b0", "\u0627\u0644\u0643\u0631\u064a\u062f\u064a", "Cr\u00e9ances"),
    "calculs": ("\U0001f9ee", "\u0627\u0644\u062d\u0627\u0633\u0628\u0629", "Calculs"),
    "prix": ("\U0001f4da", "\u0627\u0644\u0623\u0633\u0639\u0627\u0631", "Prix"),
    "reglages": ("\u2699\ufe0f", "\u0627\u0644\u0625\u0639\u062f\u0627\u062f\u0627\u062a", "R\u00e9glages"),
}

# Repli sans st.Page : 5 destinations atteignables au pouce + menu "plus".
PRINCIPALES = ["devis_express", "accueil", "annuaire", "kredi", "clients"]
COURTS = {cle: (PILULES[cle][0], PILULES[cle][1]) for cle in PRINCIPALES}

PAR_CLE = {d[1]: d for d in DEFINITIONS}


def moderne():
    """Streamlit recent : navigation multipage native disponible ?"""
    return hasattr(st, "Page") and hasattr(st, "navigation")


def construire(defaut="devis_express"):
    """Construit les objets st.Page groupes par section."""
    pages = {}
    for groupe, cle, fonction, titre, icone, url in DEFINITIONS:
        pages[cle] = st.Page(fonction, title=titre, icon=icone, url_path=url,
                             default=(cle == defaut))
    sections = {}
    for groupe, libelle in GROUPES:
        liste = [pages[d[1]] for d in DEFINITIONS if d[0] == groupe]
        if liste:
            sections[libelle] = liste
    return sections, pages


# --------------------------------------------------------- barre d'application
def barre_haut(entreprise="", courante="", liens=True):
    """Barre d'application + onglets hauts, en un seul rendu HTML.

    `liens=True` : chaque onglet est un lien vers l'URL de la page (mode
    multipage). `liens=False` : les onglets sont seulement decoratifs et la
    navigation passe par la rangee de boutons de `barre_mobile`.
    """
    definition = PAR_CLE.get(courante)
    titre_courant = definition[3] if definition else ""
    marque = ('<div class="appbar"><span class="lg">\U0001f9f0</span>'
              '<span class="tx"><b>Artisan DZ Pro</b><i>%s</i></span>%s</div>'
              % (c.e(entreprise or "\u0628\u0644\u0627 TVA \u00b7 sans taxes"),
                 ('<span class="now">%s</span>' % c.e(titre_courant)) if titre_courant else ""))

    onglets = []
    for _groupe, cle, _fonction, titre, _icone, url in DEFINITIONS:
        icone, court, court_fr = PILULES.get(cle, ("\u2022", cle, cle))
        classe = "tab on" if cle == courante else "tab"
        interieur = ('<span class="ic">%s</span>'
                     '<span class="ar" dir="rtl">%s</span>'
                     % (c.e(icone), c.e(court)))
        if liens:
            onglets.append('<a class="%s" href="%s" target="_self" title="%s">%s</a>'
                           % (classe, c.e(url), c.e(titre), interieur))
        else:
            onglets.append('<span class="%s" title="%s">%s</span>'
                           % (classe, c.e(titre), interieur))
    html = marque + '<nav class="topnav">%s</nav>' % "".join(onglets)
    st.markdown(html, unsafe_allow_html=True)
    return html


def barre_mobile(pages=None, courante=""):
    """Repli sans st.Page : 5 boutons compacts + menu \" plus \"."""
    with st.container(key="navbar"):
        colonnes = st.columns(len(PRINCIPALES) + 1)
        for colonne, cle in zip(colonnes, PRINCIPALES):
            icone, court = COURTS[cle]
            actif = (cle == courante)
            if colonne.button("%s\n%s" % (icone, court), key="nav_%s" % cle,
                              use_container_width=True,
                              type="primary" if actif else "secondary"):
                aller(cle, pages)
        secondaires = [d[1] for d in DEFINITIONS if d[1] not in PRINCIPALES]
        if colonnes[-1].button("\u22ef\n\u0627\u0644\u0645\u0632\u064a\u062f", key="nav_plus",
                               use_container_width=True,
                               type="primary" if courante in secondaires else "secondary"):
            st.session_state["menu_plus"] = True
    if st.session_state.get("menu_plus"):
        _menu_plus(pages)


@c.dialogue("\u0627\u0644\u0645\u0632\u064a\u062f \u00b7 Plus", "small")
def _menu_plus(pages=None):
    for groupe, cle, _fonction, titre, icone, _url in DEFINITIONS:
        if cle in PRINCIPALES:
            continue
        if st.button("%s  %s" % (icone, titre), key="plus_%s" % cle,
                     use_container_width=True):
            st.session_state["menu_plus"] = False
            aller(cle, pages)
    if st.button("\u0625\u063a\u0644\u0627\u0642 \u00b7 Fermer", use_container_width=True, key="plus_close"):
        st.session_state["menu_plus"] = False
        st.rerun()


def aller(cle, pages=None):
    """Changement de page, valable dans les deux modes de navigation."""
    st.session_state["page"] = cle
    st.session_state.pop("doc_ouvert", None)
    st.session_state.pop("chantier_ouvert", None)
    st.session_state["menu_plus"] = False
    if pages and cle in pages and hasattr(st, "switch_page"):
        try:
            st.switch_page(pages[cle])
            return
        except Exception:
            pass
    st.rerun()


def _cle_courante(pages, page, defaut):
    for cle, objet in pages.items():
        if objet is page or (getattr(objet, "url_path", None)
                             == getattr(page, "url_path", None)):
            return cle
    return defaut


def executer(entreprise="", defaut="devis_express"):
    """Mode moderne : st.navigation pilote l'affichage, onglets en haut."""
    sections, pages = construire(defaut)
    menu_natif = False
    try:                                   # Streamlit recent : menu masque
        page = st.navigation(sections, position="hidden")
    except Exception:                      # versions sans l'option position
        page = st.navigation(sections)
        menu_natif = True

    courante = _cle_courante(pages, page, defaut)
    st.session_state["page"] = courante or defaut

    if menu_natif:
        theme.montrer_sidebar()            # sinon aucune page ne serait atteignable
    else:
        barre_haut(entreprise, courante, liens=True)

    page.run()


def executer_repli(entreprise="", defaut="devis_express"):
    """Mode compatible (Streamlit ancien) : aiguillage par session_state."""
    courante = st.session_state.get("page", defaut)
    definition = PAR_CLE.get(courante) or PAR_CLE[defaut]
    barre_haut(entreprise, definition[1], liens=False)
    barre_mobile(None, definition[1])
    definition[2]()
