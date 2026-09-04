# -*- coding: utf-8 -*-
"""Mod\u00e8les de devis par corps de m\u00e9tier + biblioth\u00e8que de prix apprenante.

Les prix sont des ordres de grandeur du march\u00e9 alg\u00e9rien (DZD, hors taxes) :
ils servent de point de d\u00e9part et sont ensuite appris \u00e0 partir des devis r\u00e9els.
"""
from datetime import date

from . import db

# poste = (description, unite, quantite type, prix unitaire, cout materiaux/u, cout pose/u)
TEMPLATES = {
    "Peinture": {
        "icone": "\U0001f3a8",
        "couleur": "blue",
        "postes": [
            ("Protection sols et mobilier", "Forfait", 1, 4000, 1200, 800),
            ("Grattage / pr\u00e9paration des murs", "m2", 100, 250, 40, 120),
            ("Enduit de lissage 2 passes", "m2", 100, 350, 120, 90),
            ("Peinture int\u00e9rieure 2 couches", "m2", 100, 550, 180, 150),
            ("Peinture plafond 2 couches", "m2", 40, 600, 190, 170),
            ("Nettoyage fin de chantier", "Forfait", 1, 5000, 500, 2500),
        ],
    },
    "Ma\u00e7onnerie": {
        "icone": "\U0001f9f1",
        "couleur": "amber",
        "postes": [
            ("Mur en parpaing 20 cm pos\u00e9", "m2", 30, 2600, 1100, 900),
            ("Enduit ciment int\u00e9rieur", "m2", 60, 900, 300, 400),
            ("Chape de sol dos\u00e9e 350", "m2", 40, 1400, 600, 500),
            ("\u00c9vacuation des gravats", "Forfait", 1, 12000, 3000, 6000),
        ],
    },
    "Plomberie": {
        "icone": "\U0001f6bf",
        "couleur": "blue",
        "postes": [
            ("Alimentation eau PPR par point", "U", 6, 4500, 1800, 1800),
            ("\u00c9vacuation PVC par point", "U", 4, 3500, 1300, 1500),
            ("Pose sanitaire (WC / lavabo)", "U", 3, 6000, 800, 4000),
            ("Mise en eau et essais", "Forfait", 1, 5000, 0, 3500),
        ],
    },
    "\u00c9lectricit\u00e9": {
        "icone": "\u26a1",
        "couleur": "amber",
        "postes": [
            ("Point lumineux complet", "U", 8, 3200, 1200, 1400),
            ("Prise 16A encastr\u00e9e", "U", 12, 2800, 1000, 1200),
            ("Tableau divisionnaire 8 modules", "U", 1, 22000, 12000, 6000),
            ("Saign\u00e9es et rebouchage", "ml", 40, 700, 150, 400),
            ("Mise \u00e0 la terre", "Forfait", 1, 9000, 4000, 3500),
        ],
    },
    "Pl\u00e2tre / Placo": {
        "icone": "\u2b1c",
        "couleur": "grey",
        "postes": [
            ("Faux plafond placo simple", "m2", 30, 2200, 900, 900),
            ("Corniche pl\u00e2tre pos\u00e9e", "ml", 25, 900, 300, 450),
            ("Cloison placo 72 mm", "m2", 20, 2600, 1100, 1000),
            ("Enduit pl\u00e2tre de finition", "m2", 50, 700, 200, 350),
        ],
    },
    "Carrelage": {
        "icone": "\u25fb\ufe0f",
        "couleur": "green",
        "postes": [
            ("D\u00e9pose ancien carrelage", "m2", 20, 600, 0, 500),
            ("Pose carrelage sol 40x40", "m2", 40, 1200, 250, 800),
            ("Pose fa\u00efence murale", "m2", 25, 1400, 300, 950),
            ("Plinthes et joints", "ml", 30, 400, 120, 250),
        ],
    },
    "Salle de bain compl\u00e8te": {
        "icone": "\U0001f6c1",
        "couleur": "blue",
        "postes": [
            ("D\u00e9pose existant + \u00e9vacuation", "Forfait", 1, 15000, 2000, 9000),
            ("Plomberie compl\u00e8te salle de bain", "Forfait", 1, 45000, 18000, 20000),
            ("\u00c9tanch\u00e9it\u00e9 sol et douche", "m2", 8, 2200, 900, 900),
            ("Fa\u00efence murale pos\u00e9e", "m2", 22, 1400, 300, 950),
            ("Carrelage sol", "m2", 8, 1300, 280, 850),
            ("Pose sanitaires et robinetterie", "Forfait", 1, 18000, 2000, 12000),
        ],
    },
    "\u00c9tanch\u00e9it\u00e9 terrasse": {
        "icone": "\U0001f327\ufe0f",
        "couleur": "green",
        "postes": [
            ("Nettoyage et primaire d'accroche", "m2", 60, 350, 120, 180),
            ("Chape de pente", "m2", 60, 1200, 500, 500),
            ("Membrane bitumineuse 2 couches", "m2", 60, 1900, 900, 700),
            ("Relev\u00e9s et finitions", "ml", 30, 900, 300, 450),
        ],
    },
}

ORDRE_TEMPLATES = ["Peinture", "Ma\u00e7onnerie", "Plomberie", "\u00c9lectricit\u00e9",
                   "Pl\u00e2tre / Placo", "Carrelage", "Salle de bain compl\u00e8te",
                   "\u00c9tanch\u00e9it\u00e9 terrasse"]

# Metier choisi au premier lancement -> modeles et prestations a mettre en avant
CORRESPONDANCE_METIER = {
    "Peintre": ["Peinture"],
    "Ma\u00e7on": ["Ma\u00e7onnerie", "\u00c9tanch\u00e9it\u00e9 terrasse"],
    "Plombier": ["Plomberie", "Salle de bain compl\u00e8te"],
    "\u00c9lectricien": ["\u00c9lectricit\u00e9"],
    "Pl\u00e2trier": ["Pl\u00e2tre / Placo", "Peinture"],
    "Carreleur": ["Carrelage", "Salle de bain compl\u00e8te"],
    "Multi-services": [],
}


def _normaliser(texte):
    """Minuscules sans accents : 'Electricien' == '\u00e9lectricien'."""
    import unicodedata
    return "".join(ch for ch in unicodedata.normalize("NFD", (texte or "").lower())
                   if unicodedata.category(ch) != "Mn").strip()


def metiers_artisan():
    """Modeles lies au metier declare (onboarding ou Reglages).
    Tolerant aux accents, majuscules et formes du type 'peintre en batiment'.
    [] = tout montrer."""
    brut = _normaliser(db.get_param("entreprise_metier"))
    if not brut:
        return []
    for cle, metiers in CORRESPONDANCE_METIER.items():
        cible = _normaliser(cle)
        if brut == cible or brut.startswith(cible) or (len(brut) >= 4 and cible.startswith(brut)):
            return metiers
    return []


def templates_ordonnes():
    """Retourne (modeles du metier d'abord, autres metiers ensuite)."""
    metiers = metiers_artisan()
    if not metiers:
        return list(ORDRE_TEMPLATES), []
    principaux = [n for n in ORDRE_TEMPLATES if n in metiers]
    autres = [n for n in ORDRE_TEMPLATES if n not in metiers]
    return principaux, autres


def suggestions_metier(limite=80):
    """Suggestions de postes pour l'editeur de devis.

    Ordre : 1) prestations deja vendues liees au metier (prix appris),
    2) prestations des modeles du metier (meme si la bibliotheque est vide),
    3) le reste de la bibliotheque.
    """
    lignes = bibliotheque("", limite)
    metiers = metiers_artisan()
    if not metiers:
        return lignes
    connus = {l.get("libelle") for l in lignes}
    modeles = []
    for nom in metiers:
        for description, unite, _q, pu, cmat, cpose in TEMPLATES.get(nom, {}).get("postes", []):
            if description not in connus:
                modeles.append({"libelle": description, "unite": unite, "prix_unitaire": pu,
                                "cout_materiaux": cmat, "cout_pose": cpose, "metier": nom})
                connus.add(description)
    libelles_metier = {m["libelle"] for m in modeles}
    du_metier = [l for l in lignes if (l.get("metier") or "") in metiers
                 or (l.get("libelle") or "") in libelles_metier]
    autres = [l for l in lignes if l not in du_metier]
    return du_metier + modeles + autres


def postes_template(nom):
    """Retourne les postes d'un mod\u00e8le sous forme de lignes de devis.

    Si la prestation existe deja dans la bibliotheque de prix (donc deja
    vendue par l'artisan), on reprend SON prix plutot que le prix indicatif.
    """
    modele = TEMPLATES.get(nom)
    if not modele:
        return []
    lignes = []
    for description, unite, qte, pu, cmat, cpose in modele["postes"]:
        appris = db.one("SELECT * FROM catalogue WHERE libelle=? AND unite=?", (description, unite))
        if appris:
            pu = appris["prix_unitaire"] or pu
            cmat = appris["cout_materiaux"] or cmat
            cpose = appris["cout_pose"] or cpose
        lignes.append(ligne_vide(description, unite, qte, pu, cmat, cpose))
    return lignes


def ligne_vide(description="", unite="U", quantite=1.0, prix=0.0, cout_mat=0.0, cout_pose=0.0):
    return {
        "id": None,
        "description": description,
        "unite": unite,
        "quantite": float(quantite),
        "prix_unitaire": float(prix),
        "cout_materiaux": float(cout_mat),
        "cout_pose": float(cout_pose),
    }


# ------------------------------------------------------- bibliotheque de prix
def apprendre(lignes, metier=None):
    """Memorise chaque prestation vendue : la biblioth\u00e8que grandit toute seule."""
    for l in lignes:
        libelle = (l.get("description") or "").strip()
        if not libelle:
            continue
        db.run(
            "INSERT INTO catalogue (libelle, metier, unite, prix_unitaire, cout_materiaux, cout_pose, usages, dernier_usage) "
            "VALUES (?,?,?,?,?,?,1,?) "
            "ON CONFLICT(libelle, unite) DO UPDATE SET "
            "  prix_unitaire=excluded.prix_unitaire, "
            "  cout_materiaux=excluded.cout_materiaux, "
            "  cout_pose=excluded.cout_pose, "
            "  metier=COALESCE(excluded.metier, catalogue.metier), "
            "  usages=catalogue.usages+1, "
            "  dernier_usage=excluded.dernier_usage",
            (libelle, metier, l.get("unite") or "U", float(l.get("prix_unitaire") or 0),
             float(l.get("cout_materiaux") or 0), float(l.get("cout_pose") or 0),
             date.today().isoformat()))


def bibliotheque(recherche="", limite=40):
    if recherche:
        return db.q("SELECT * FROM catalogue WHERE libelle LIKE ? "
                    "ORDER BY usages DESC, dernier_usage DESC LIMIT ?",
                    ("%" + recherche + "%", limite))
    return db.q("SELECT * FROM catalogue ORDER BY usages DESC, dernier_usage DESC LIMIT ?", (limite,))


def prestations_connues():
    """Libell\u00e9s connus (biblioth\u00e8que + mod\u00e8les) pour l'auto-compl\u00e9tion et l'analyse Eclair."""
    connus = {}
    for nom, modele in TEMPLATES.items():
        for description, unite, _q, pu, cmat, cpose in modele["postes"]:
            connus[description.lower()] = ligne_vide(description, unite, 1, pu, cmat, cpose)
    for row in db.q("SELECT * FROM catalogue"):
        connus[row["libelle"].lower()] = ligne_vide(
            row["libelle"], row["unite"], 1, row["prix_unitaire"],
            row["cout_materiaux"], row["cout_pose"])
    return connus


# ------------------------------------------------------- amorcage / import de prix
def ensemencer(metiers=None):
    """Pr\u00e9-remplit la biblioth\u00e8que de prix : listes officielles (fichier Excel)
    + postes des mod\u00e8les du m\u00e9tier. Jamais d'\u00e9crasement : un prix d\u00e9j\u00e0 appris
    est conserv\u00e9 (ON CONFLICT DO NOTHING). Retourne le nombre de nouveaut\u00e9s."""
    from .prix_seed import PRIX_METIERS
    cibles = metiers or list(TEMPLATES.keys())
    avant = db.scalar("SELECT COUNT(*) FROM catalogue") or 0
    for nom in cibles:
        for libelle, prix in PRIX_METIERS.get(nom, []):
            db.run("INSERT INTO catalogue "
                   "(libelle, metier, unite, prix_unitaire, cout_materiaux, cout_pose, usages, dernier_usage) "
                   "VALUES (?,?,?,?,0,0,0,?) ON CONFLICT(libelle, unite) DO NOTHING",
                   (libelle, nom, "U", float(prix), date.today().isoformat()))
        for poste in TEMPLATES.get(nom, {}).get("postes", []):
            description, unite, _q, pu, cmat, cpose = poste
            db.run("INSERT INTO catalogue "
                   "(libelle, metier, unite, prix_unitaire, cout_materiaux, cout_pose, usages, dernier_usage) "
                   "VALUES (?,?,?,?,?,?,0,?) ON CONFLICT(libelle, unite) DO NOTHING",
                   (description, nom, unite, float(pu), float(cmat), float(cpose),
                    date.today().isoformat()))
    apres = db.scalar("SELECT COUNT(*) FROM catalogue") or 0
    return int(apres - avant)


def importer_prix(fichier, metier):
    """Importe une liste de prix Excel (.xlsx) ou CSV dans la biblioth\u00e8que.

    R\u00e8gle de d\u00e9tection : d\u00e9signation = colonne contenant 'signation' sinon
    premi\u00e8re colonne texte ; prix = colonne contenant '\u062f\u062c' / 'DZD' / '\u0645\u062d\u0648\u0644'
    sinon derni\u00e8re colonne num\u00e9rique. Les prix existants sont conserv\u00e9s."""
    import pandas as pd
    nom = (getattr(fichier, "name", "") or "").lower()
    df = pd.read_csv(fichier) if nom.endswith(".csv") else pd.read_excel(fichier)

    col_lib = None
    for col in df.columns:
        if "signation" in str(col).lower():
            col_lib = col
            break
    if col_lib is None:
        for col in df.columns:
            if df[col].dtype == object:
                col_lib = col
                break

    col_prix = None
    for col in reversed(list(df.columns)):
        if any(mot in str(col) for mot in ("\u062f\u062c", "DZD", "\u0645\u062d\u0648\u0644")) \
                and pd.api.types.is_numeric_dtype(df[col]):
            col_prix = col
            break
    if col_prix is None:
        numeriques = [c0 for c0 in df.columns if pd.api.types.is_numeric_dtype(df[c0])]
        col_prix = numeriques[-1] if numeriques else None
    if col_lib is None or col_prix is None:
        return 0

    avant = db.scalar("SELECT COUNT(*) FROM catalogue") or 0
    for _, row in df.iterrows():
        libelle = str(row[col_lib] or "").strip()
        try:
            prix = float(row[col_prix])
        except (TypeError, ValueError):
            continue
        if not libelle or prix <= 0:
            continue
        db.run("INSERT INTO catalogue "
               "(libelle, metier, unite, prix_unitaire, cout_materiaux, cout_pose, usages, dernier_usage) "
               "VALUES (?,?,?,?,0,0,0,?) ON CONFLICT(libelle, unite) DO NOTHING",
               (libelle, metier, "U", prix, date.today().isoformat()))
    apres = db.scalar("SELECT COUNT(*) FROM catalogue") or 0
    return int(apres - avant)
