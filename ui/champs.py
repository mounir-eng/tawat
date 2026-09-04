# -*- coding: utf-8 -*-
"""Champs bilingues : libellé vertical (arabe gras au-dessus, français gris dessous).

Avant :   "الاسم / Nom"           -> deux langues qui se battent sur une ligne
Après :   الاسم                     -> arabe gras, lisible en premier
          Nom                          -> français discret, en sous-titre

Chaque fonction dessine le libellé puis le widget Streamlit avec
`label_visibility="collapsed"`, ce qui garantit un alignement identique partout.
"""
import streamlit as st

from core import wilayas
from . import components as c


# ------------------------------------------------------------------- libelle
def label(arabe, francais="", requis=False, aide="", icone=""):
    """Libellé vertical bilingue. Retourne le HTML dessiné (utile aux tests)."""
    morceaux = ['<div class="lab2">']
    if icone:
        morceaux.append('<span class="ic">%s</span>' % c.e(icone))
    morceaux.append('<span class="tx">')
    morceaux.append('<span class="ar" dir="rtl">%s</span>' % c.e(arabe or ""))
    if francais:
        morceaux.append('<span class="fr">%s</span>' % c.e(francais))
    morceaux.append("</span>")
    if requis:
        morceaux.append('<span class="req">*</span>')
    if aide:
        morceaux.append('<span class="hint" title="%s">?</span>' % c.e(aide))
    morceaux.append("</div>")
    html = "".join(morceaux)
    st.markdown(html, unsafe_allow_html=True)
    return html


def bloc_titre(arabe, francais="", icone=""):
    """Titre de section, même grammaire visuelle que les libellés."""
    html = ('<div class="sec2">%s<span class="ar" dir="rtl">%s</span>'
            '<span class="fr">%s</span></div>'
            % ('<span class="ic">%s</span>' % c.e(icone) if icone else "",
               c.e(arabe or ""), c.e(francais or "")))
    st.markdown(html, unsafe_allow_html=True)
    return html


def libelle_option(code, texte_option):
    """Option de sélecteur numérotée proprement : "[03] Villa"."""
    try:
        return "[%02d] %s" % (int(code), texte_option)
    except (TypeError, ValueError):
        return str(texte_option)


# -------------------------------------------------------------------- interne
def _plat(arabe, francais):
    """Libellé texte (lecteurs d'écran) : le visuel passe par label()."""
    parties = [t for t in ((arabe or "").strip(), (francais or "").strip()) if t]
    return " \u00b7 ".join(parties) or " "


def _widget(fonction, arabe, francais, kw, options=None):
    kw.setdefault("label_visibility", "collapsed")
    if options is None:
        return fonction(_plat(arabe, francais), **kw)
    return fonction(_plat(arabe, francais), options, **kw)


# --------------------------------------------------------------------- champs
def texte(arabe, francais="", requis=False, aide="", icone="", **kw):
    label(arabe, francais, requis, aide, icone)
    return _widget(st.text_input, arabe, francais, kw)


def zone(arabe, francais="", requis=False, aide="", icone="", **kw):
    label(arabe, francais, requis, aide, icone)
    kw.setdefault("height", 88)
    return _widget(st.text_area, arabe, francais, kw)


def nombre(arabe, francais="", requis=False, aide="", icone="", **kw):
    label(arabe, francais, requis, aide, icone)
    kw.setdefault("step", 1.0)
    return _widget(st.number_input, arabe, francais, kw)


def montant(arabe, francais="", pas=500.0, requis=False, aide="", icone="\U0001f4b0", **kw):
    """Montant en dinars : pas de 500 DZD, jamais de valeur négative."""
    label(arabe, francais, requis, aide, icone)
    kw.setdefault("min_value", 0.0)
    kw.setdefault("step", float(pas))
    return _widget(st.number_input, arabe, francais, kw)


def choix(arabe, francais="", options=(), requis=False, aide="", icone="", **kw):
    label(arabe, francais, requis, aide, icone)
    return _widget(st.selectbox, arabe, francais, kw, list(options))


def multi(arabe, francais="", options=(), requis=False, aide="", icone="", **kw):
    label(arabe, francais, requis, aide, icone)
    return _widget(st.multiselect, arabe, francais, kw, list(options))


def radio(arabe, francais="", options=(), requis=False, aide="", icone="", **kw):
    label(arabe, francais, requis, aide, icone)
    kw.setdefault("horizontal", True)
    return _widget(st.radio, arabe, francais, kw, list(options))


def segments(arabe, francais="", options=(), requis=False, aide="", icone="", **kw):
    """Boutons segmentés si la version le permet, sinon boutons radio."""
    label(arabe, francais, requis, aide, icone)
    fonction = getattr(st, "segmented_control", None)
    if fonction is None:
        kw.setdefault("horizontal", True)
        return _widget(st.radio, arabe, francais, kw, list(options))
    return _widget(fonction, arabe, francais, kw, list(options))


def bascule(arabe, francais="", requis=False, aide="", icone="", **kw):
    label(arabe, francais, requis, aide, icone)
    fonction = getattr(st, "toggle", st.checkbox)
    return _widget(fonction, arabe, francais, kw)


def date_(arabe, francais="", requis=False, aide="", icone="\U0001f4c5", **kw):
    label(arabe, francais, requis, aide, icone)
    kw.setdefault("format", "DD/MM/YYYY")
    return _widget(st.date_input, arabe, francais, kw)


def wilaya(arabe="\u0627\u0644\u0648\u0644\u0627\u064a\u0629", francais="Wilaya", avec_vide=True,
           vide=wilayas.VIDE, requis=False, aide="", **kw):
    """Sélecteur de wilaya : options formatées "[16] الجزائر - Alger".

    Retourne le code (int) ou None : c'est ce qui est stocké en base.
    """
    label(arabe, francais, requis, aide, "\U0001f4cd")
    kw.setdefault("format_func", lambda code: wilayas.libelle(code, vide))
    return _widget(st.selectbox, arabe, francais, kw, wilayas.options(avec_vide))
