# -*- coding: utf-8 -*-
"""Regles metier : numerotation, totaux, marges, rentabilite, kredi, relances."""
from datetime import date, timedelta

from . import db
from .fmt import dz, jours_depuis, date_fr

PREFIXES = {"Devis": "DV", "Facture": "FA", "Recu": "RC"}

# Parcours de vie d'un document (le "stepper" de l'interface)
ETAPES = ["Brouillon", "Envoye", "Accepte", "Facture", "Paye"]
ETAPES_LIB = {
    "Brouillon": "Brouillon",
    "Envoye": "Envoy\u00e9",
    "Accepte": "Accept\u00e9",
    "Facture": "Factur\u00e9",
    "Paye": "Pay\u00e9",
    "Annule": "Annul\u00e9",
}
COULEUR_STATUT = {
    "Brouillon": "grey",
    "Envoye": "blue",
    "Accepte": "green",
    "Facture": "amber",
    "Paye": "green",
    "Annule": "red",
}

MODES_PAIEMENT = ["Esp\u00e8ces", "Versement CCP / BaridiMob", "Ch\u00e8que", "Virement"]
TYPES_TRAVAUX = ["Peinture", "Ma\u00e7onnerie", "Plomberie", "\u00c9lectricit\u00e9",
                 "Pl\u00e2tre / Placo", "Carrelage", "\u00c9tanch\u00e9it\u00e9", "Menuiserie", "Autre"]
UNITES = ["U", "m2", "ml", "m3", "Forfait", "Jour", "Sac", "Kg", "L", "Lot"]


# ------------------------------------------------------------------ numeros
def nouveau_numero(type_doc="Devis"):
    prefixe = PREFIXES.get(type_doc, "DV")
    annee = date.today().year
    motif = "%s-%d-%%" % (prefixe, annee)
    n = db.scalar("SELECT COUNT(*) FROM devis_factures WHERE numero LIKE ?", (motif,))
    for i in range(int(n) + 1, int(n) + 500):
        numero = "%s-%d-%03d" % (prefixe, annee, i)
        if not db.one("SELECT id FROM devis_factures WHERE numero=?", (numero,)):
            return numero
    return "%s-%d-%d" % (prefixe, annee, int(n) + 1)


# ------------------------------------------------------------------ totaux
def total_lignes(lignes):
    total = 0.0
    for l in lignes:
        total += float(l.get("quantite") or 0) * float(l.get("prix_unitaire") or 0)
    return total


def cout_lignes(lignes):
    """Cout interne previsionnel (materiaux + pose), jamais montre au client."""
    cout = 0.0
    for l in lignes:
        qte = float(l.get("quantite") or 0)
        cout += qte * (float(l.get("cout_materiaux") or 0) + float(l.get("cout_pose") or 0))
    return cout


def marge_ligne(l):
    """Retourne (marge_dzd, marge_pct or None)."""
    qte = float(l.get("quantite") or 0)
    pv = qte * float(l.get("prix_unitaire") or 0)
    pr = qte * (float(l.get("cout_materiaux") or 0) + float(l.get("cout_pose") or 0))
    if pr <= 0:
        return pv, None
    marge = pv - pr
    return marge, (marge / pv * 100 if pv else 0.0)


def total_document(document_id, remise=None):
    lignes = db.q("SELECT * FROM lignes_document WHERE document_id=?", (document_id,))
    if remise is None:
        doc = db.one("SELECT remise FROM devis_factures WHERE id=?", (document_id,))
        remise = (doc or {}).get("remise") or 0
    return max(0.0, total_lignes(lignes) - float(remise or 0))


def recalcul_total(document_id):
    total = total_document(document_id)
    db.run("UPDATE devis_factures SET total=? WHERE id=?", (total, document_id))
    return total


def total_paye(document_id):
    return float(db.scalar("SELECT COALESCE(SUM(montant),0) FROM paiements WHERE document_id=?",
                           (document_id,)))


def reste_a_payer(doc):
    return max(0.0, float(doc.get("total") or 0) - total_paye(doc["id"]))


def sante_marge(marge_pct):
    """Classe une marge : 'green' / 'amber' / 'red' selon la cible parametree."""
    cible = db.get_param_num("marge_cible", 30)
    if marge_pct is None:
        return "grey", "Co\u00fbt non saisi"
    if marge_pct >= cible:
        return "green", "Saine"
    if marge_pct >= cible / 2:
        return "amber", "Basse"
    return "red", "Risque"


# ------------------------------------------------------------------ chantier
def rentabilite(chantier_id):
    encaisse = float(db.scalar("SELECT COALESCE(SUM(montant),0) FROM paiements WHERE chantier_id=?",
                               (chantier_id,)))
    if encaisse == 0:
        encaisse = float(db.scalar(
            "SELECT COALESCE(SUM(p.montant),0) FROM paiements p "
            "JOIN devis_factures f ON f.id = p.document_id WHERE f.chantier_id=?", (chantier_id,)))
    materiaux = float(db.scalar("SELECT COALESCE(SUM(montant),0) FROM depenses_materiaux WHERE chantier_id=?",
                                (chantier_id,)))
    mo = float(db.scalar("SELECT COALESCE(SUM(montant),0) FROM paie_main_oeuvre WHERE chantier_id=?",
                         (chantier_id,)))
    facture = float(db.scalar(
        "SELECT COALESCE(SUM(total),0) FROM devis_factures "
        "WHERE chantier_id=? AND type_doc IN ('Facture','Recu')", (chantier_id,)))
    if facture == 0:
        facture = float(db.scalar(
            "SELECT COALESCE(SUM(total),0) FROM devis_factures WHERE chantier_id=? AND statut IN ('Accepte','Facture','Paye')",
            (chantier_id,)))
    depenses = materiaux + mo
    benefice = encaisse - depenses
    return {
        "encaisse": encaisse,
        "materiaux": materiaux,
        "main_oeuvre": mo,
        "depenses": depenses,
        "benefice": benefice,
        "marge": (benefice / encaisse * 100) if encaisse else 0.0,
        "facture": facture,
        "reste_client": max(0.0, facture - encaisse),
    }


# ------------------------------------------------------------------ tableau de bord
def bornes_mois(reference=None):
    ref = reference or date.today()
    debut = ref.replace(day=1)
    fin = (debut + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    return debut.isoformat(), fin.isoformat()


def kpis_mois():
    debut, fin = bornes_mois()
    encaisse = float(db.scalar(
        "SELECT COALESCE(SUM(montant),0) FROM paiements WHERE date_paiement BETWEEN ? AND ?",
        (debut, fin)))
    materiaux = float(db.scalar(
        "SELECT COALESCE(SUM(montant),0) FROM depenses_materiaux WHERE date_achat BETWEEN ? AND ?",
        (debut, fin)))
    mo = float(db.scalar(
        "SELECT COALESCE(SUM(montant),0) FROM paie_main_oeuvre WHERE date_paie BETWEEN ? AND ?",
        (debut, fin)))
    kredi = total_kredi()
    return {
        "encaisse": encaisse,
        "depenses": materiaux + mo,
        "materiaux": materiaux,
        "main_oeuvre": mo,
        "benefice": encaisse - materiaux - mo,
        "kredi": kredi,
        "marge": ((encaisse - materiaux - mo) / encaisse * 100) if encaisse else 0.0,
    }


def documents_avec_reste():
    """Documents factures/acceptes dont il reste de l'argent a encaisser."""
    docs = db.q(
        "SELECT f.*, c.nom AS client, c.telephone AS tel, ch.nom AS chantier "
        "FROM devis_factures f "
        "LEFT JOIN clients c ON c.id = f.client_id "
        "LEFT JOIN chantiers ch ON ch.id = f.chantier_id "
        "WHERE f.statut NOT IN ('Brouillon','Annule') ORDER BY f.date_doc")
    sortie = []
    for doc in docs:
        paye = total_paye(doc["id"])
        reste = float(doc.get("total") or 0) - paye
        if reste > 1:
            doc["paye"] = paye
            doc["reste"] = reste
            doc["retard"] = jours_depuis(doc.get("echeance") or doc.get("date_doc"))
            sortie.append(doc)
    sortie.sort(key=lambda x: -x["retard"])
    return sortie


def total_kredi():
    return sum(d["reste"] for d in documents_avec_reste())


# ------------------------------------------------------------------ relances
def ton_relance(retard):
    if retard < 7:
        return "doux"
    if retard < 30:
        return "normal"
    return "ferme"


def message_relance(doc, langue="fr", ton=None):
    """Genere un texte de relance pret a coller dans WhatsApp / Viber."""
    ton = ton or ton_relance(doc.get("retard", 0))
    client = (doc.get("client") or "").split(" ")[0] or ""
    entreprise = db.get_param("entreprise_nom") or ""
    reste = dz(doc.get("reste", 0))
    total = dz(doc.get("total", 0))
    num = doc.get("numero", "")
    chantier = doc.get("chantier") or ""

    if langue == "ar":
        base = {
            "doux": "\u0635\u0628\u0627\u062d \u0627\u0644\u062e\u064a\u0631 {c}\u060c \u062a\u0630\u0643\u064a\u0631 \u0628\u0633\u064a\u0637 \u0641\u0642\u0637 : \u0628\u0627\u0642\u064a {r} \u0645\u0646 {t} \u0639\u0644\u0649 {ch}. \u0642\u0648\u0644\u064a \u0648\u0642\u062a\u0627\u0634 \u064a\u0646\u0627\u0633\u0628\u0643 \u0648\u0646\u062f\u064a\u0631\u0648\u0647\u0627. \u0628\u0627\u0631\u0643 \u0627\u0644\u0644\u0647 \u0641\u064a\u0643 \U0001f64f",
            "normal": "\u0627\u0644\u0633\u0644\u0627\u0645 {c}\u060c \u0628\u0627\u0642\u064a {r} \u0645\u0646 \u0645\u062c\u0645\u0648\u0639 {t} \u0639\u0644\u0649 \u0627\u0644\u0641\u0627\u062a\u0648\u0631\u0629 {n}. \u0645\u0646 \u0641\u0636\u0644\u0643 \u062d\u062f\u062f\u0644\u064a \u062a\u0627\u0631\u064a\u062e \u0628\u0627\u0634 \u0646\u0648\u0635\u064a \u0627\u0644\u062d\u0633\u0627\u0628. \u0634\u0643\u0631\u0627 \u0644\u0643.",
            "ferme": "\u0627\u0644\u0633\u0644\u0627\u0645 {c}\u060c \u0627\u0644\u0641\u0627\u062a\u0648\u0631\u0629 {n} \u0628\u0627\u0642\u064a \u0641\u064a\u0647\u0627 {r} \u0648\u0639\u0646\u062f\u0647\u0627 \u062a\u0623\u062e\u064a\u0631 {j} \u064a\u0648\u0645. \u0631\u0627\u0646\u064a \u0645\u062d\u062a\u0627\u062c \u0627\u0644\u062e\u0644\u0627\u0635 \u0628\u0627\u0634 \u0646\u0643\u0645\u0644 \u0627\u0644\u062e\u062f\u0645\u0629. \u0646\u0633\u062a\u0646\u0627\u0643 \u0627\u0644\u064a\u0648\u0645.",
        }[ton]
    else:
        base = {
            "doux": "Bonjour {c}, petit rappel amical : il reste {r} sur {t} pour {ch}. "
                    "Dites-moi quand cela vous arrange, sans probl\u00e8me. Merci beaucoup \U0001f64f",
            "normal": "Bonjour {c}, concernant la facture {n} : il reste {r} sur un total de {t}. "
                      "Pouvez-vous me confirmer une date de r\u00e8glement ? Merci d'avance.",
            "ferme": "Bonjour {c}, la facture {n} affiche un retard de {j} jours et un solde de {r}. "
                     "J'ai besoin de ce r\u00e8glement pour poursuivre le chantier. "
                     "Merci de me r\u00e9pondre aujourd'hui.",
        }[ton]

    texte = base.format(c=client, r=reste, t=total, n=num,
                        ch=chantier or num, j=max(0, doc.get("retard", 0)))
    if entreprise:
        texte += "\n" + entreprise
    return texte


def message_devis(doc):
    entreprise = db.get_param("entreprise_nom") or ""
    validite = int(db.get_param_num("validite_devis", 30))
    client = (doc.get("client") or "").split(" ")[0]
    return ("Bonjour {c}, voici le devis {n} pour {ch} : {t}, sans TVA. "
            "Valable {v} jours. Le PDF est en pi\u00e8ce jointe. "
            "Dites-moi si on lance les travaux \U0001f44d\n{e}").format(
        c=client, n=doc.get("numero", ""), ch=doc.get("chantier") or "vos travaux",
        t=dz(doc.get("total", 0)), v=validite, e=entreprise)


def message_recu(doc, montant):
    client = (doc.get("client") or "").split(" ")[0]
    return "Bonjour %s, bien re\u00e7u %s le %s pour %s. Merci ! Reste : %s." % (
        client, dz(montant), date_fr(date.today().isoformat()),
        doc.get("numero", ""), dz(doc.get("reste", 0)))
