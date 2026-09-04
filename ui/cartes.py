# -*- coding: utf-8 -*-
"""Listings en cartes CSS : un artisan / un client par carte, 3 actions par carte.

Performance : toute une grille est envoyée à Streamlit en UN seul rendu HTML
(pas un widget par ligne), et le clic « profil » passe par un lien interne
?fiche=<id> lu par ui/etat.depuis_url().
"""
try:
    from urllib.parse import quote
except ImportError:                                    # pragma: no cover
    from urllib import quote

import streamlit as st

from core import wilayas
from core.fmt import initiales, nombre, tel_joli
from . import components as c

CLASSES_COULEUR = {"red": "k-red", "green": "k-green", "amber": "k-amber",
                   "grey": "k-grey", "blue": ""}


# ------------------------------------------------------------------- telephone
def _numero(telephone):
    """0661 22 33 44 -> +213661223344 (jamais d'espace dans un lien)."""
    brut = "".join(ch for ch in str(telephone or "") if ch.isdigit() or ch == "+")
    if not brut:
        return ""
    if brut.startswith("+"):
        return brut
    if brut.startswith("00"):
        return "+" + brut[2:]
    if brut.startswith("213"):
        return "+" + brut
    return "+213" + brut.lstrip("0")


def _whatsapp(telephone, texte=""):
    numero = _numero(telephone)
    if not numero:
        return ""
    lien = "https://wa.me/" + numero.lstrip("+")
    if texte:
        lien += "?text=" + quote(texte)
    return lien


def message_baridimob(entreprise, rip, montant=None, client=""):
    """Message de paiement prêt à envoyer (BaridiMob / CCP)."""
    lignes = []
    if client:
        lignes.append("\u0627\u0644\u0633\u0644\u0627\u0645 \u0639\u0644\u064a\u0643\u0645 %s" % client)
    lignes.append("\u062f\u0641\u0639 \u0639\u0628\u0631 BaridiMob \u00b7 Paiement par BaridiMob")
    if montant:
        lignes.append("\u0627\u0644\u0645\u0628\u0644\u063a \u00b7 Montant : %s DZD" % nombre(montant))
    lignes.append("RIP : %s" % rip)
    if entreprise:
        lignes.append(entreprise)
    lignes.append("\u0634\u0643\u0631\u0627 \u00b7 Merci")
    return "\n".join(lignes)


# --------------------------------------------------------------------- actions
def _action(icone, arabe, francais, url, classe, actif=True, infobulle="",
            nouvel_onglet=True):
    interieur = ('<span class="ic">%s</span><span class="tx">'
                 '<b dir="rtl">%s</b><i>%s</i></span>'
                 % (c.e(icone), c.e(arabe), c.e(francais)))
    if not actif or not url:
        return ('<span class="act off" title="%s">%s</span>'
                % (c.e(infobulle or francais), interieur))
    cible = ' target="_blank" rel="noopener"' if nouvel_onglet else ""
    return ('<a class="act %s" href="%s"%s title="%s">%s</a>'
            % (classe, c.e(url), cible, c.e(infobulle or francais), interieur))


def barre_actions(telephone, entreprise="", rip="", montant=None, nom="", message=""):
    """Appeler · WhatsApp · BaridiMob — toujours trois emplacements, même inactifs."""
    numero = _numero(telephone)
    appel = _action("\U0001f4de", "\u0627\u062a\u0635\u0644", "Appeler",
                    ("tel:" + numero) if numero else "", "call", bool(numero),
                    infobulle="" if numero else "Num\u00e9ro manquant",
                    nouvel_onglet=False)
    whatsapp = _action("\U0001f4ac", "\u0648\u0627\u062a\u0633\u0627\u0628", "WhatsApp",
                       _whatsapp(telephone, message), "wa", bool(numero),
                       infobulle="" if numero else "Num\u00e9ro manquant")
    lien_paiement = ""
    if rip and numero:
        lien_paiement = _whatsapp(telephone,
                                  message_baridimob(entreprise, rip, montant, nom))
    baridi = _action("\U0001f3e6", "\u0628\u0631\u064a\u062f\u064a \u0645\u0648\u0628", "BaridiMob",
                     lien_paiement, "bm", bool(lien_paiement),
                     infobulle="" if lien_paiement else "RIP \u00e0 remplir dans R\u00e9glages")
    return '<div class="acts">%s%s%s</div>' % (appel, whatsapp, baridi)


def _etoiles(note):
    try:
        valeur = float(note or 0)
    except (TypeError, ValueError):
        valeur = 0.0
    if valeur <= 0:
        return ""
    pleines = int(round(valeur))
    etoiles = "\u2605" * max(0, min(5, pleines)) + "\u2606" * max(0, 5 - pleines)
    return '<span class="note">%s <b>%s</b></span>' % (etoiles, ("%.1f" % valeur))


# ---------------------------------------------------------------------- carte
def carte(fiche, entreprise="", rip="", parametre="fiche"):
    """HTML d'une carte. `fiche` : dict simple (voir ui/views/annuaire.py)."""
    couleur = CLASSES_COULEUR.get(fiche.get("couleur") or "blue", "")
    nom = fiche.get("nom") or ""
    sous = fiche.get("nom_fr") or fiche.get("sous_titre") or ""

    tags = []
    if fiche.get("metier"):
        tags.append('<span class="tag m">%s</span>' % c.e(fiche["metier"]))
    if fiche.get("wilaya"):
        tags.append('<span class="tag w">%s</span>' % c.e(wilayas.libelle(fiche["wilaya"], "")))
    for extra in (fiche.get("tags") or []):
        if extra:
            tags.append('<span class="tag">%s</span>' % c.e(extra))

    montant = ""
    if fiche.get("montant"):
        montant = ('<div class="mny"><b>%s</b><i>%s</i></div>'
                   % (nombre(fiche["montant"]),
                      c.e(fiche.get("montant_libelle") or "DZD")))

    badge = ""
    if fiche.get("badge"):
        badge = '<span class="dispo%s">%s</span>' % (
            "" if fiche.get("disponible", True) else " no", c.e(fiche["badge"]))
    elif fiche.get("alerte"):
        badge = '<span class="dispo no">\u0645\u062a\u0623\u062e\u0631 \u00b7 en retard</span>'

    telephone = fiche.get("telephone") or ""
    lien_profil = "?%s=%s" % (parametre, fiche.get("id"))
    return (
        '<article class="kart %s">'
        '<a class="prof" href="%s" title="\u0627\u0644\u0645\u0644\u0641 \u00b7 Voir la fiche">'
        '<div class="tete"><span class="av">%s</span>'
        '<span class="idt"><b dir="rtl">%s</b><i>%s</i>'
        '<span class="sous">%s</span></span>%s</div>'
        '<div class="tags">%s</div>%s</a>%s</article>'
        % (couleur, c.e(lien_profil), c.e(initiales(nom or sous)),
           c.e(nom), c.e(sous), c.e(tel_joli(telephone) or ""),
           _etoiles(fiche.get("note")) + badge,
           "".join(tags), montant,
           barre_actions(telephone, entreprise, rip, fiche.get("montant"),
                         nom or sous, fiche.get("message") or "")))


def grille(fiches, entreprise="", rip="", parametre="fiche"):
    """Dessine toute la liste en un seul rendu. Retourne le nombre de cartes."""
    morceaux = [carte(f, entreprise, rip, parametre) for f in (fiches or [])]
    if not morceaux:
        return 0
    st.markdown('<div class="karts">%s</div>' % "".join(morceaux),
                unsafe_allow_html=True)
    return len(morceaux)


def bandeau_resultats(nombre_resultats, arabe, francais, actifs=0):
    """Ligne discrète « 12 حرفي · artisan(s) — 2 filtres » au-dessus de la grille."""
    filtres = ""
    if actifs:
        filtres = ('<span class="flt">%d \u0645\u0631\u0634\u062d \u00b7 filtre(s)</span>' % actifs)
    html = ('<div class="resline"><b>%s</b><span dir="rtl">%s</span>'
            '<i>%s</i>%s</div>'
            % (nombre(nombre_resultats), c.e(arabe), c.e(francais), filtres))
    st.markdown(html, unsafe_allow_html=True)
    return html


def puces_filtres(elements):
    """Rangee de puces qui resume les filtres actifs (un seul rendu HTML).

    `elements` : liste de couples (texte, actif). Rien ne s'affiche si la liste
    est vide, ce qui garde le haut d'ecran respirant quand aucun filtre n'est
    pose.
    """
    morceaux = []
    for texte, actif in (elements or []):
        if not texte:
            continue
        morceaux.append('<span class="chip%s"><span class="ar">%s</span></span>'
                        % (" on" if actif else "", c.e(texte)))
    if not morceaux:
        return ""
    html = '<div class="fbar">%s</div>' % "".join(morceaux)
    st.markdown(html, unsafe_allow_html=True)
    return html
