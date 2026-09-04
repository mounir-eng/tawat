# -*- coding: utf-8 -*-
"""الحرفيون · Annuaire des artisans et sous-traitants (données locales).

Aucune donnée fictive : la liste se remplit avec les artisans que l'utilisateur
saisit lui-même (équipe, sous-traitants, collègues de confiance).
"""
from datetime import date

from . import db

METIERS = [
    "\u0643\u0647\u0631\u0628\u0627\u0626\u064a - \u00c9lectricien",
    "\u0628\u0646\u0627\u0621 - Ma\u00e7on",
    "\u0633\u0628\u0627\u0643 - Plombier",
    "\u062f\u0647\u0627\u0646 - Peintre",
    "\u062c\u0628\u0627\u0633 - Pl\u00e2trier",
    "\u0628\u0644\u0627\u0637 - Carreleur",
    "\u0646\u062c\u0627\u0631 - Menuisier",
    "\u062d\u062f\u0627\u062f - Ferronnier",
    "\u0623\u0644\u0645\u0646\u064a\u0648\u0645 - Aluminium",
    "\u062a\u0643\u064a\u064a\u0641 - Climatisation",
    "\u0623\u0634\u063a\u0627\u0644 \u0639\u0627\u0645\u0629 - Multi-services",
    "\u0639\u0627\u0645\u0644 - Man\u0153uvre",
]

TRIS = {
    "nom": "nom COLLATE NOCASE ASC",
    "note": "note DESC, tarif_jour ASC",
    "tarif": "(CASE WHEN ifnull(tarif_jour,0)=0 THEN 1 ELSE 0 END), tarif_jour ASC",
    "recent": "id DESC",
}

COLONNES = ("nom", "nom_fr", "metier", "wilaya", "commune", "telephone",
            "tarif_jour", "note", "specialites", "disponible", "rip", "remarque")


# ------------------------------------------------------------------- lecture
def lister(recherche="", metier=None, wilaya=None, dispo_seulement=False, tri="nom"):
    sql = "SELECT * FROM artisans WHERE 1=1"
    params = []
    motif = (recherche or "").strip().lower()
    if motif:
        sql += (" AND (lower(nom) LIKE ? OR lower(ifnull(nom_fr,'')) LIKE ?"
                " OR ifnull(telephone,'') LIKE ?"
                " OR lower(ifnull(specialites,'')) LIKE ?"
                " OR lower(ifnull(commune,'')) LIKE ?)")
        params += ["%" + motif + "%"] * 5
    if metier:
        sql += " AND metier = ?"
        params.append(metier)
    if wilaya:
        sql += " AND wilaya = ?"
        params.append(int(wilaya))
    if dispo_seulement:
        sql += " AND ifnull(disponible,1) = 1"
    return db.q(sql + " ORDER BY " + TRIS.get(tri, TRIS["nom"]), tuple(params))


def charger(artisan_id):
    return db.one("SELECT * FROM artisans WHERE id=?", (artisan_id,))


def metiers_utilises():
    lignes = db.q("SELECT DISTINCT metier FROM artisans "
                  "WHERE ifnull(metier,'') <> '' ORDER BY metier")
    return [ligne["metier"] for ligne in lignes]


def wilayas_utilisees():
    lignes = db.q("SELECT DISTINCT wilaya FROM artisans "
                  "WHERE ifnull(wilaya,0) > 0 ORDER BY wilaya")
    return [int(ligne["wilaya"]) for ligne in lignes]


def statistiques():
    ligne = db.one(
        "SELECT COUNT(*) AS total, "
        "SUM(CASE WHEN ifnull(disponible,1)=1 THEN 1 ELSE 0 END) AS dispo, "
        "COUNT(DISTINCT metier) AS metiers, "
        "AVG(CASE WHEN ifnull(tarif_jour,0)>0 THEN tarif_jour END) AS tarif "
        "FROM artisans") or {}
    return {
        "total": int(ligne.get("total") or 0),
        "disponibles": int(ligne.get("dispo") or 0),
        "metiers": int(ligne.get("metiers") or 0),
        "tarif_moyen": float(ligne.get("tarif") or 0),
    }


# ------------------------------------------------------------------ ecriture
def enregistrer(donnees, artisan_id=None):
    """Crée ou met à jour une fiche. Retourne l'identifiant."""
    valeurs = [_valeur(nom, donnees.get(nom)) for nom in COLONNES]
    if artisan_id:
        db.run("UPDATE artisans SET %s WHERE id=?"
               % ", ".join("%s=?" % nom for nom in COLONNES),
               tuple(valeurs) + (artisan_id,))
        return artisan_id
    return db.run("INSERT INTO artisans (%s, date_creation) VALUES (%s, ?)"
                  % (", ".join(COLONNES), ", ".join(["?"] * len(COLONNES))),
                  tuple(valeurs) + (date.today().isoformat(),))


def supprimer(artisan_id):
    db.run("DELETE FROM artisans WHERE id=?", (artisan_id,))


def basculer_dispo(artisan_id):
    """Inverse la disponibilité et retourne le nouvel état (0 ou 1)."""
    fiche = charger(artisan_id)
    if not fiche:
        return 0
    nouveau = 0 if int(fiche.get("disponible") or 0) else 1
    db.run("UPDATE artisans SET disponible=? WHERE id=?", (nouveau, artisan_id))
    return nouveau


def _valeur(nom, brute):
    if nom in ("tarif_jour", "note"):
        try:
            return float(brute or 0)
        except (TypeError, ValueError):
            return 0.0
    if nom == "disponible":
        return 1 if (brute in (True, 1, "1") or brute is None) else 0
    if nom == "wilaya":
        try:
            return int(brute) if brute else None
        except (TypeError, ValueError):
            return None
    return ("" if brute is None else str(brute)).strip()
