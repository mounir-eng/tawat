# -*- coding: utf-8 -*-
"""Compatibilite entre versions de Streamlit (PC 1.4x <-> Streamlit Cloud 1.6x).

Streamlit remplace progressivement `use_container_width=True` par
`width="stretch"`. Sur les versions recentes, l'ancien parametre provoque une
erreur et l'application ne demarre plus ("Oh no. Error running app.").

Ce module traduit l'ancien parametre en nouveau, uniquement si la version
installee ne l'accepte plus. Le meme code fonctionne donc en local et en ligne.
"""
import inspect

import streamlit as st

# Widgets et conteneurs susceptibles de recevoir use_container_width.
FONCTIONS = (
    "button", "download_button", "form_submit_button", "link_button", "page_link",
    "dataframe", "data_editor", "table", "image", "metric", "json", "code",
    "text_input", "text_area", "number_input", "selectbox", "multiselect",
    "radio", "checkbox", "toggle", "slider", "select_slider", "date_input",
    "time_input", "file_uploader", "color_picker", "camera_input", "chat_input",
    "pills", "segmented_control", "feedback", "plotly_chart", "altair_chart",
    "vega_lite_chart", "pydeck_chart", "bar_chart", "line_chart", "area_chart",
    "scatter_chart", "map", "audio", "video", "expander", "popover", "container",
)

_FAIT = False


def _accepte(fonction, parametre):
    """Vrai si la fonction accepte ce parametre (ou un **kwargs generique)."""
    try:
        parametres = inspect.signature(fonction).parameters
    except (TypeError, ValueError):
        return True
    if parametre in parametres:
        return True
    return any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parametres.values())


def _adapter(fonction):
    accepte_width = _accepte(fonction, "width")

    def enveloppe(*args, **kwargs):
        if "use_container_width" in kwargs:
            valeur = kwargs.pop("use_container_width")
            if accepte_width and "width" not in kwargs:
                kwargs["width"] = "stretch" if valeur else "content"
        return fonction(*args, **kwargs)

    enveloppe.__name__ = getattr(fonction, "__name__", "compat")
    enveloppe.__doc__ = getattr(fonction, "__doc__", None)
    enveloppe._artisan_compat = True
    return enveloppe


def activer():
    """A appeler une fois au demarrage, avant le premier affichage."""
    global _FAIT
    if _FAIT:
        return 0
    _FAIT = True

    cibles = [st]
    try:  # les colonnes / conteneurs passent par cette classe
        from streamlit.delta_generator import DeltaGenerator
        cibles.append(DeltaGenerator)
    except Exception:      # pragma: no cover - version inconnue
        pass

    corrigees = 0
    for cible in cibles:
        for nom in FONCTIONS:
            fonction = getattr(cible, nom, None)
            if fonction is None or getattr(fonction, "_artisan_compat", False):
                continue
            if _accepte(fonction, "use_container_width"):
                continue
            try:
                setattr(cible, nom, _adapter(fonction))
                corrigees += 1
            except (AttributeError, TypeError):  # pragma: no cover
                continue
    return corrigees
