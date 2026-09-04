# -*- coding: utf-8 -*-
"""Devis \u00c9clair : transforme une phrase parl\u00e9e artisan en lignes de devis.

Exemples reconnus :
    "45 m2 peinture 550"                 -> 45 m2 \u00d7 550
    "12 prises 2800 + 8 points lumineux" -> deux lignes
    "faux plafond 30 m2 a 2200"
    "forfait nettoyage 5000"
"""
import re

from .catalog import ligne_vide, prestations_connues

UNITES_TEXTE = {
    "m2": "m2", "m\u00b2": "m2", "metre carre": "m2", "m\u00e8tre carr\u00e9": "m2",
    "ml": "ml", "metre": "ml", "m\u00e8tre": "ml", "metres": "ml", "m": "ml",
    "m3": "m3", "m\u00b3": "m3",
    "u": "U", "unite": "U", "unit\u00e9": "U", "piece": "U", "pi\u00e8ce": "U", "pcs": "U",
    "sac": "Sac", "sacs": "Sac", "kg": "Kg", "l": "L", "litre": "L",
    "jour": "Jour", "jours": "Jour", "j": "Jour",
    "forfait": "Forfait", "lot": "Lot",
}

MOTS_METIER = {
    "peinture": ("Peinture int\u00e9rieure 2 couches", "m2", 550),
    "peindre": ("Peinture int\u00e9rieure 2 couches", "m2", 550),
    "enduit": ("Enduit de lissage 2 passes", "m2", 350),
    "plafond": ("Faux plafond placo simple", "m2", 2200),
    "placo": ("Cloison placo 72 mm", "m2", 2600),
    "platre": ("Enduit pl\u00e2tre de finition", "m2", 700),
    "pl\u00e2tre": ("Enduit pl\u00e2tre de finition", "m2", 700),
    "corniche": ("Corniche pl\u00e2tre pos\u00e9e", "ml", 900),
    "carrelage": ("Pose carrelage sol 40x40", "m2", 1200),
    "faience": ("Pose fa\u00efence murale", "m2", 1400),
    "fa\u00efence": ("Pose fa\u00efence murale", "m2", 1400),
    "plinthe": ("Plinthes et joints", "ml", 400),
    "prise": ("Prise 16A encastr\u00e9e", "U", 2800),
    "prises": ("Prise 16A encastr\u00e9e", "U", 2800),
    "lumiere": ("Point lumineux complet", "U", 3200),
    "lumineux": ("Point lumineux complet", "U", 3200),
    "tableau": ("Tableau divisionnaire 8 modules", "U", 22000),
    "saignee": ("Saign\u00e9es et rebouchage", "ml", 700),
    "parpaing": ("Mur en parpaing 20 cm pos\u00e9", "m2", 2600),
    "chape": ("Chape de sol dos\u00e9e 350", "m2", 1400),
    "etancheite": ("Membrane bitumineuse 2 couches", "m2", 1900),
    "\u00e9tanch\u00e9it\u00e9": ("Membrane bitumineuse 2 couches", "m2", 1900),
    "wc": ("Pose sanitaire (WC / lavabo)", "U", 6000),
    "lavabo": ("Pose sanitaire (WC / lavabo)", "U", 6000),
    "sanitaire": ("Pose sanitaire (WC / lavabo)", "U", 6000),
    "evacuation": ("\u00c9vacuation PVC par point", "U", 3500),
    "nettoyage": ("Nettoyage fin de chantier", "Forfait", 5000),
    "gravats": ("\u00c9vacuation des gravats", "Forfait", 12000),
    "demolition": ("D\u00e9pose existant + \u00e9vacuation", "Forfait", 15000),
}

_NOMBRE = re.compile(r"(\d+(?:[.,]\d+)?)")


def _f(txt):
    return float(str(txt).replace(",", "."))


def _decouper(phrase):
    morceaux = re.split(r"[\n;+]|(?:\s+et\s+)|(?:\s+puis\s+)|,", phrase)
    return [m.strip() for m in morceaux if m and m.strip()]


def analyser_segment(segment):
    """Retourne une ligne de devis (dict) ou None."""
    txt = segment.strip().lower()
    if not txt:
        return None

    nombres = [_f(n) for n in _NOMBRE.findall(txt)]
    mots = re.findall(r"[a-z\u00e0-\u00ff\u00b2\u00b3]+", txt)

    # 1. prestation reconnue ?
    base = None
    connues = prestations_connues()
    for libelle, modele in connues.items():
        if libelle in txt:
            base = dict(modele)
            break
    if base is None:
        for mot in mots:
            if mot in MOTS_METIER:
                description, unite, pu = MOTS_METIER[mot]
                base = ligne_vide(description, unite, 1, pu)
                break
    if base is None:
        nettoye = re.sub(r"\d+(?:[.,]\d+)?", " ", segment).strip(" -\u00b7")
        nettoye = re.sub(r"\s{2,}", " ", nettoye)
        if not nettoye:
            return None
        base = ligne_vide(nettoye.capitalize(), "U", 1, 0)

    # 2. unite explicite dans le texte ?
    for cle, unite in UNITES_TEXTE.items():
        if re.search(r"\b%s\b" % re.escape(cle), txt):
            base["unite"] = unite
            break

    # 3. quantite et prix : le plus grand nombre est le prix, le premier la quantite
    if len(nombres) >= 2:
        base["quantite"] = nombres[0]
        base["prix_unitaire"] = max(nombres[1:])
    elif len(nombres) == 1:
        valeur = nombres[0]
        if valeur >= 1000 and base.get("prix_unitaire"):
            base["prix_unitaire"] = valeur
        elif valeur >= 1000:
            base["prix_unitaire"] = valeur
            base["quantite"] = 1
        else:
            base["quantite"] = valeur
    if base["unite"] == "Forfait":
        base["quantite"] = 1
    base["description"] = base["description"][:120]
    return base


def analyser(phrase):
    """Phrase libre -> liste de lignes de devis."""
    lignes = []
    for segment in _decouper(phrase or ""):
        ligne = analyser_segment(segment)
        if ligne:
            lignes.append(ligne)
    return lignes
