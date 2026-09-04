# -*- coding: utf-8 -*-
"""Cycle de vie des documents : cr\u00e9ation, sauvegarde des lignes, conversion, paiements."""
from datetime import date, timedelta

from . import catalog, db
from .metier import ETAPES, nouveau_numero, recalcul_total, total_paye


def creer_document(client_id=None, chantier_id=None, type_doc="Devis", lignes=None, note=""):
    validite = int(db.get_param_num("validite_devis", 30))
    doc_id = db.run(
        "INSERT INTO devis_factures (numero,type_doc,client_id,chantier_id,date_doc,statut,remise,total,note,echeance) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (nouveau_numero(type_doc), type_doc, client_id, chantier_id, date.today().isoformat(),
         "Brouillon", 0, 0, note,
         (date.today() + timedelta(days=validite)).isoformat()))
    if lignes:
        remplacer_lignes(doc_id, lignes)
    return doc_id


def charger_document(doc_id):
    return db.one(
        "SELECT f.*, c.nom AS client, c.telephone AS tel, ch.nom AS chantier "
        "FROM devis_factures f LEFT JOIN clients c ON c.id=f.client_id "
        "LEFT JOIN chantiers ch ON ch.id=f.chantier_id WHERE f.id=?", (doc_id,))


def charger_lignes(doc_id):
    return db.q("SELECT * FROM lignes_document WHERE document_id=? ORDER BY ordre, id", (doc_id,))


def remplacer_lignes(doc_id, lignes):
    """\u00c9crit les lignes du document puis met \u00e0 jour le total et la biblioth\u00e8que de prix."""
    db.run("DELETE FROM lignes_document WHERE document_id=?", (doc_id,))
    propres = []
    for i, l in enumerate(lignes):
        description = (l.get("description") or "").strip()
        if not description:
            continue
        qte = float(l.get("quantite") or 0)
        pu = float(l.get("prix_unitaire") or 0)
        propres.append((doc_id, i, description, qte, l.get("unite") or "U", pu,
                        float(l.get("cout_materiaux") or 0), float(l.get("cout_pose") or 0),
                        qte * pu, (l.get("piece") or "").strip() or None,
                        (l.get("niveau") or "").strip() or None))
    if propres:
        db.runmany(
            "INSERT INTO lignes_document "
            "(document_id,ordre,description,quantite,unite,prix_unitaire,cout_materiaux,cout_pose,"
            "total_ligne,piece,niveau) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)", propres)
        metier = db.scalar("SELECT ch.type_travaux FROM devis_factures d "
                           "LEFT JOIN chantiers ch ON ch.id = d.chantier_id WHERE d.id=?",
                           (doc_id,), "")
        if not metier:
            metiers = catalog.metiers_artisan()
            metier = metiers[0] if metiers else None
        catalog.apprendre(lignes, metier)
    return recalcul_total(doc_id)


def changer_statut(doc_id, statut):
    db.run("UPDATE devis_factures SET statut=? WHERE id=?", (statut, doc_id))


def statut_suivant(statut):
    if statut in ("Paye", "Annule"):
        return None
    if statut not in ETAPES:
        return "Envoye"
    i = ETAPES.index(statut)
    return ETAPES[i + 1] if i + 1 < len(ETAPES) else None


def convertir(doc_id, type_cible="Facture"):
    """Transforme un devis en facture ou re\u00e7u : m\u00eames lignes, nouveau num\u00e9ro."""
    doc = db.one("SELECT * FROM devis_factures WHERE id=?", (doc_id,))
    if not doc:
        return None
    delai = 15
    nouveau = db.run(
        "INSERT INTO devis_factures (numero,type_doc,client_id,chantier_id,date_doc,statut,remise,"
        "total,note,echeance,type_batiment,mode_prix) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (nouveau_numero(type_cible), type_cible, doc["client_id"], doc["chantier_id"],
         date.today().isoformat(), "Facture" if type_cible == "Facture" else "Paye",
         doc["remise"], doc["total"], doc["note"],
         (date.today() + timedelta(days=delai)).isoformat(), doc.get("type_batiment"),
         doc.get("mode_prix") or "pose"))
    for l in charger_lignes(doc_id):
        db.run("INSERT INTO lignes_document "
               "(document_id,ordre,description,quantite,unite,prix_unitaire,cout_materiaux,"
               "cout_pose,total_ligne,piece,niveau) "
               "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
               (nouveau, l["ordre"], l["description"], l["quantite"], l["unite"],
                l["prix_unitaire"], l["cout_materiaux"], l["cout_pose"], l["total_ligne"],
                l.get("piece"), l.get("niveau")))
    recalcul_total(nouveau)
    changer_statut(doc_id, "Facture" if type_cible == "Facture" else doc["statut"])
    return nouveau


def dupliquer(doc_id):
    doc = db.one("SELECT * FROM devis_factures WHERE id=?", (doc_id,))
    if not doc:
        return None
    nouveau = creer_document(doc["client_id"], doc["chantier_id"], doc["type_doc"], None, doc["note"])
    lignes = [dict(l) for l in charger_lignes(doc_id)]
    remplacer_lignes(nouveau, lignes)
    db.run("UPDATE devis_factures SET remise=? WHERE id=?", (doc["remise"], nouveau))
    recalcul_total(nouveau)
    return nouveau


def supprimer(doc_id):
    db.run("DELETE FROM devis_factures WHERE id=?", (doc_id,))


def enregistrer_paiement(doc_id, montant, mode="Esp\u00e8ces", quand=None, note=""):
    doc = db.one("SELECT * FROM devis_factures WHERE id=?", (doc_id,))
    db.run("INSERT INTO paiements (document_id,chantier_id,montant,date_paiement,mode,note) "
           "VALUES (?,?,?,?,?,?)",
           (doc_id, (doc or {}).get("chantier_id"), float(montant),
            (quand or date.today()).isoformat() if hasattr(quand or date.today(), "isoformat") else str(quand),
            mode, note))
    if doc:
        total = float(doc.get("total") or 0)
        if total_paye(doc_id) >= total - 1 and total > 0:
            changer_statut(doc_id, "Paye")
        elif (doc.get("statut") or "") in ("Brouillon", "Envoye", "Accepte"):
            changer_statut(doc_id, "Accepte")


def documents(recherche="", type_doc=None, statut=None, limite=200):
    sql = ("SELECT f.*, c.nom AS client, c.telephone AS tel, ch.nom AS chantier, "
           "(SELECT COUNT(*) FROM lignes_document l WHERE l.document_id=f.id) AS nb_lignes "
           "FROM devis_factures f LEFT JOIN clients c ON c.id=f.client_id "
           "LEFT JOIN chantiers ch ON ch.id=f.chantier_id WHERE 1=1")
    params = []
    if type_doc:
        sql += " AND f.type_doc=?"
        params.append(type_doc)
    if statut:
        sql += " AND f.statut=?"
        params.append(statut)
    if recherche:
        sql += " AND (f.numero LIKE ? OR c.nom LIKE ? OR ch.nom LIKE ?)"
        motif = "%" + recherche + "%"
        params += [motif, motif, motif]
    sql += " ORDER BY date(f.date_doc) DESC, f.id DESC LIMIT ?"
    params.append(limite)
    return db.q(sql, tuple(params))
