# -*- coding: utf-8 -*-
"""Composants d'interface r\u00e9utilisables : pilules, cartes, h\u00e9ros, bandeaux KPI\u2026

v4 : ajout des libell\u00e9s bilingues (arabe + fran\u00e7ais), du bandeau de KPI,
des tuiles d'actions et de la barre de progression \u00ab avancement \u00bb.
"""
import html

import streamlit as st

from core.fmt import dz, initiales, nombre
from core.metier import ETAPES, ETAPES_LIB, COULEUR_STATUT
from .theme import COULEURS_PILULE, JETONS


def e(txt):
    return html.escape(str(txt if txt is not None else ""))


def bi(ar, fr="", *args):
    """Libell\u00e9 bilingue : arabe d'abord, fran\u00e7ais entre parenth\u00e8ses.

    Les placeholders (%d, %s\u2026) sont format\u00e9s S\u00c9PAR\u00c9MENT dans chaque langue :
    bi("%d \u062e\u062f\u0645\u0629", "%d prestations", 12) -> "12 \u062e\u062f\u0645\u0629 (12 prestations)".
    Ne jamais faire bi(ar, fr) % valeur : le libell\u00e9 combin\u00e9 contiendrait 2 placeholders."""
    if args:
        ar = ar % args
        if fr:
            fr = fr % args
    return ar if not fr else ar + " (" + fr + ")"


# ------------------------------------------------------------------ atomes
def pilule(texte, couleur="grey"):
    fond, encre = COULEURS_PILULE.get(couleur, COULEURS_PILULE["grey"])
    return '<span class="pill" style="background:%s;color:%s">%s</span>' % (fond, encre, e(texte))


def avatar(nom, couleur="blue"):
    fond, encre = COULEURS_PILULE.get(couleur, COULEURS_PILULE["blue"])
    return '<div class="av" style="background:%s;color:%s">%s</div>' % (fond, encre, e(initiales(nom)))


def section(titre, lien=""):
    droite = '<span class="lien">%s</span>' % e(lien) if lien else ""
    st.markdown('<div class="sec">%s%s</div>' % (e(titre), droite), unsafe_allow_html=True)


def html_bloc(markup):
    st.markdown(markup, unsafe_allow_html=True)


def entete(titre, sous_titre="", pilule_droite=None):
    droite = ('<div style="margin-left:auto">%s</div>' % pilule_droite) if pilule_droite else ""
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin:2px 0 12px">'
        '<div><div style="font-size:1.45rem;font-weight:800;letter-spacing:-.015em;color:%s">%s</div>'
        '<div class="sm muted">%s</div></div>%s</div>'
        % (JETONS["encre"], e(titre), e(sous_titre), droite),
        unsafe_allow_html=True)


def salutation(entreprise, nb_alertes=0):
    """Bandeau de bienvenue : logo, nom de l'app, bonjour, cloche de notification."""
    from datetime import datetime
    heure = datetime.now().hour
    bonjour = "\u0635\u0628\u0627\u062d \u0627\u0644\u062e\u064a\u0631" if 5 <= heure < 18 \
        else "\u0645\u0633\u0627\u0621 \u0627\u0644\u062e\u064a\u0631"
    badge = '<div class="badge">%d</div>' % nb_alertes if nb_alertes else ""
    st.markdown(
        '<div class="greet">'
        '<div class="logo">\U0001f9f0</div>'
        '<div><div class="app">%s</div><div class="salut">%s\u060c %s \U0001f44b</div></div>'
        '<div class="cloche">\U0001f514%s</div>'
        '</div>' % (e(entreprise or "Artisan DZ Pro"), bonjour, e(entreprise or ""), badge),
        unsafe_allow_html=True)


def hero(label, valeur, unite="DZD", cases=()):
    cases_html = ""
    if cases:
        cases_html = '<div class="split">' + "".join(
            '<div><div class="k">%s</div><div class="v" style="color:%s">%s</div></div>'
            % (e(k), coul or "#fff", e(v)) for k, v, coul in cases) + "</div>"
    st.markdown(
        '<div class="hero"><div class="lbl">%s</div>'
        '<div class="val">%s<small>%s</small></div>%s</div>'
        % (e(label), e(valeur), e(unite), cases_html), unsafe_allow_html=True)


def bande_kpi(items):
    """Bandeau blanc de 3 mini-cartes KPI. items = [dict(icone,label,valeur,sous,accent,lien)]."""
    cartes = ""
    for it in items:
        accent = " warn" if it.get("accent") else ""
        lien = ('<div class="lien">%s \u2190</div>' % e(it["lien"])) if it.get("lien") else ""
        cartes += ('<div class="kpi2%s"><div class="top"><div class="ic">%s</div>'
                   '<div class="lab">%s</div></div>'
                   '<div class="val">%s<small>%s</small></div><div class="cap">%s</div>%s</div>'
                   % (accent, it.get("icone", ""), e(it["label"]), e(it["valeur"]),
                      e(it.get("unite", "")), e(it.get("sous", "")), lien))
    st.markdown('<div class="band">%s</div>' % cartes, unsafe_allow_html=True)


def tuiles(items):
    """Grille de tuiles d'actions. items = [(icone, label, action_callable)]."""
    with st.container(key="tuiles"):
        for ligne in range(0, len(items), 3):
            colonnes = st.columns(3)
            for col, (icone, label, action) in zip(colonnes, items[ligne:ligne + 3]):
                if col.button("%s\n%s" % (icone, label), key="tuile_%s" % label,
                              use_container_width=True):
                    action()


def barre_progression(pct, couleur=None):
    pct = max(0.0, min(100.0, float(pct or 0)))
    style = "background:%s" % couleur if couleur else ""
    st.markdown('<div class="prog"><i style="width:%.1f%%;%s"></i></div>' % (pct, style),
                unsafe_allow_html=True)


def barre_repartition(parts, legende=True):
    """parts = [(libelle, montant, couleur_hex)]"""
    total = sum(max(0.0, float(p[1] or 0)) for p in parts) or 1.0
    segments = "".join('<i style="width:%.2f%%;background:%s"></i>'
                       % (max(0.0, float(m or 0)) / total * 100, c) for _l, m, c in parts)
    leg = ""
    if legende:
        leg = '<div class="leg">' + "".join(
            '<span><b style="background:%s"></b>%s %s</span>' % (c, e(l), nombre(m))
            for l, m, c in parts) + "</div>"
    st.markdown('<div class="bar">%s</div>%s' % (segments, leg), unsafe_allow_html=True)


def etapes(statut):
    """Petit indicateur de progression Brouillon -> Pay\u00e9."""
    if statut == "Annule":
        return '<div class="step"><span>%s</span></div>' % ETAPES_LIB["Annule"]
    idx = ETAPES.index(statut) if statut in ETAPES else 0
    barres = "".join('<i class="%s"></i>' % ("on" if i <= idx else "") for i in range(len(ETAPES)))
    return '<div class="step">%s<span>%s</span></div>' % (barres, e(ETAPES_LIB.get(statut, statut)))


def vide(icone, titre, sous_titre=""):
    st.markdown('<div class="empty"><div class="ic">%s</div><div class="t">%s</div>'
                '<div class="s">%s</div></div>' % (icone, e(titre), e(sous_titre)),
                unsafe_allow_html=True)


def message_copiable(texte):
    st.markdown('<div class="msg">%s</div>' % e(texte), unsafe_allow_html=True)


def ligne_stat(libelle, valeur, couleur=None):
    st.markdown('<div style="display:flex;justify-content:space-between;padding:5px 0">'
                '<span class="sm muted">%s</span><span class="money" style="color:%s">%s</span></div>'
                % (e(libelle), couleur or JETONS["texte"], e(valeur)), unsafe_allow_html=True)


def stats3(colonnes):
    """3 mini-statistiques dans une carte chantier : [(label, valeur)]."""
    cellules = "".join('<div><div class="l">%s</div><div class="v">%s</div></div>'
                       % (e(l), e(v)) for l, v in colonnes)
    st.markdown('<div class="st3">%s</div>' % cellules, unsafe_allow_html=True)


# ------------------------------------------------------------------ cartes
def carte_document(doc, reste=None):
    """Carte de devis/facture : identit\u00e9 \u00e0 gauche, argent \u00e0 droite, \u00e9tape en bas."""
    statut = doc.get("statut") or "Brouillon"
    couleur = COULEUR_STATUT.get(statut, "grey")
    sous = " \u00b7 ".join([x for x in [doc.get("chantier") or "", "%d postes" % (doc.get("nb_lignes") or 0)] if x])
    reste_html = ""
    if reste and reste > 1:
        reste_html = '<div class="xs" style="color:%s;font-weight:650">Reste %s</div>' % (
            JETONS["rouge"], dz(reste, False))
    st.markdown(
        '<div class="row" style="align-items:flex-start">%s'
        '<div style="flex:1;min-width:0">'
        '  <div class="num">%s</div><div class="nm">%s</div><div class="ds">%s</div>%s'
        '</div>'
        '<div style="text-align:right"><div class="money" style="font-size:16px">%s</div>'
        '<div class="xs muted">DZD</div><div style="margin-top:6px">%s</div>%s</div></div>'
        % (avatar(doc.get("client") or "?", couleur),
           e(doc.get("numero") or ""), e(doc.get("client") or "Sans client"), e(sous),
           etapes(statut), nombre(doc.get("total") or 0),
           pilule(ETAPES_LIB.get(statut, statut), couleur), reste_html),
        unsafe_allow_html=True)


def carte_contact(nom, sous_titre, montant=None, couleur="blue", suffixe=""):
    droite = ""
    if montant is not None:
        droite = ('<div style="text-align:right"><div class="money">%s</div>'
                  '<div class="xs muted">%s</div></div>' % (nombre(montant), e(suffixe or "DZD")))
    st.markdown('<div class="row">%s<div style="flex:1;min-width:0">'
                '<div class="nm">%s</div><div class="ds">%s</div></div>%s</div>'
                % (avatar(nom, couleur), e(nom), e(sous_titre), droite), unsafe_allow_html=True)


# ------------------------------------------------------------------ widgets
def pilules_filtre(label, options, cle, defaut=None):
    """Filtres en pilules avec repli automatique selon la version de Streamlit."""
    if hasattr(st, "pills"):
        choix = st.pills(label, options, selection_mode="single", default=defaut or options[0],
                         key=cle, label_visibility="collapsed")
        return choix or (defaut or options[0])
    if hasattr(st, "segmented_control"):
        choix = st.segmented_control(label, options, default=defaut or options[0], key=cle,
                                     label_visibility="collapsed")
        return choix or (defaut or options[0])
    return st.radio(label, options, horizontal=True, key=cle, label_visibility="collapsed")


def dialogue(titre, largeur="small"):
    """D\u00e9corateur de bo\u00eete de dialogue, avec repli sur un conteneur si indisponible.
    Fen\u00eatres volontairement \u00e9troites : l'utilisateur ne perd jamais le contexte."""
    if hasattr(st, "dialog"):
        return st.dialog(titre, width=largeur)

    def faux_decorateur(fn):
        def wrapper(*a, **kw):
            with st.container(border=True):
                st.subheader(titre)
                return fn(*a, **kw)
        return wrapper
    return faux_decorateur


def bouton_lien(label, url, icone="", cle=None, type_="secondary"):
    if not url:
        st.button("%s %s" % (icone, label), disabled=True, use_container_width=True, key=cle)
        return
    st.link_button("%s %s" % (icone, label), url, use_container_width=True, type=type_)


def toast(texte, icone="\u2705"):
    if hasattr(st, "toast"):
        st.toast(texte, icon=icone)
    else:
        st.success(texte)
