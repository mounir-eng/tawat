# -*- coding: utf-8 -*-
"""Mémoire d'écran (st.session_state) : filtres de recherche et fiche ouverte.

Problème résolu : la valeur d'un widget Streamlit disparaît de session_state dès
qu'il n'est plus affiché (changement de page, dialogue fermé). On garde donc
deux magasins :

    f:<espace>:<nom>   valeur retenue du filtre (persiste d'une page à l'autre)
    w:<espace>:<nom>   clé du widget lui-même (volatile)
    p:<espace>         identifiant du profil / de la fiche ouverte

Usage type :
    champs.texte("بحث", "Rechercher", **etat.lie("annuaire", "q", ""))
"""
import streamlit as st

PREFIXE_FILTRE = "f:"
PREFIXE_WIDGET = "w:"
PREFIXE_PROFIL = "p:"


def cle_filtre(espace, nom):
    return "%s%s:%s" % (PREFIXE_FILTRE, espace, nom)


def cle_widget(espace, nom):
    return "%s%s:%s" % (PREFIXE_WIDGET, espace, nom)


# ------------------------------------------------------------------- filtres
def filtre(espace, nom, defaut=None):
    """Valeur courante d'un filtre, même si son widget n'est pas à l'écran."""
    cle = cle_filtre(espace, nom)
    if cle in st.session_state:
        return st.session_state[cle]
    volatile = cle_widget(espace, nom)
    if volatile in st.session_state:
        return st.session_state[volatile]
    return defaut


def poser(espace, nom, valeur):
    """Force une valeur de filtre (magasin durable + widget)."""
    st.session_state[cle_filtre(espace, nom)] = valeur
    st.session_state[cle_widget(espace, nom)] = valeur
    return valeur


def lie(espace, nom, defaut=None):
    """Arguments à passer à un widget pour qu'il se souvienne de sa valeur.

    Retourne {"key": ..., "on_change": ...} : jamais de `value=`, ce qui
    éviterait l'avertissement Streamlit sur les clés déjà présentes.
    """
    volatile = cle_widget(espace, nom)
    durable = cle_filtre(espace, nom)
    if volatile not in st.session_state:
        st.session_state[volatile] = filtre(espace, nom, defaut)

    def _synchroniser():
        st.session_state[durable] = st.session_state.get(volatile)

    return {"key": volatile, "on_change": _synchroniser}


def reinitialiser(espace, defauts):
    """Remet tous les filtres d'un écran à leur valeur par défaut."""
    for nom, valeur in (defauts or {}).items():
        st.session_state[cle_filtre(espace, nom)] = valeur
        st.session_state.pop(cle_widget(espace, nom), None)
    fermer(espace)


def nb_actifs(espace, defauts):
    """Nombre de filtres qui ne sont plus à leur valeur par défaut."""
    total = 0
    for nom, defaut in (defauts or {}).items():
        valeur = filtre(espace, nom, defaut)
        if isinstance(valeur, str) and isinstance(defaut, str):
            different = valeur.strip() != defaut.strip()
        else:
            different = valeur != defaut
        if different and valeur not in (None, "", False):
            total += 1
    return total


# -------------------------------------------------------- fiche / profil ouvert
def ouvrir(espace, identifiant):
    st.session_state[PREFIXE_PROFIL + espace] = identifiant
    return identifiant


def ouvert(espace):
    return st.session_state.get(PREFIXE_PROFIL + espace)


def fermer(espace):
    st.session_state.pop(PREFIXE_PROFIL + espace, None)


def depuis_url(espace, parametre="fiche"):
    """Ouvre la fiche demandée par un lien de carte (?fiche=12) puis nettoie l'URL.

    Permet aux cartes HTML d'être cliquables sans bouton Streamlit : c'est ce qui
    rend la grille légère (un seul rendu pour toute la liste).
    """
    try:
        parametres = st.query_params
    except Exception:
        return ouvert(espace)
    try:
        brut = parametres.get(parametre)
    except Exception:
        return ouvert(espace)
    if brut in (None, ""):
        return ouvert(espace)
    if isinstance(brut, (list, tuple)):
        brut = brut[0] if brut else ""
    valeur = brut
    try:
        valeur = int(str(brut).strip())
    except (TypeError, ValueError):
        pass
    ouvrir(espace, valeur)
    try:
        del parametres[parametre]
    except Exception:
        pass
    return valeur


# ------------------------------------------------------------------- divers
def memoire(nom, defaut=None):
    """Petit état global (hors filtres) avec valeur initiale."""
    if nom not in st.session_state:
        st.session_state[nom] = defaut
    return st.session_state[nom]
