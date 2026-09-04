# -*- coding: utf-8 -*-
"""Jeu de d\u00e9monstration r\u00e9aliste (Alger) : clients, chantiers, devis, d\u00e9penses, paiements.

Usage :  python demo_data.py
"""
import os
import sys
from datetime import date, timedelta

RACINE = os.path.dirname(os.path.abspath(__file__))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from core import catalog, db, docs  # noqa: E402


def jour(decalage):
    return (date.today() + timedelta(days=decalage)).isoformat()


def main():
    db.init()
    db.set_param("entreprise_nom", "Ets. Ma\u00efz \u2014 Peinture & Rev\u00eatement")
    db.set_param("entreprise_metier", "Peintre")
    db.set_param("entreprise_tel", "0555 12 34 56")
    db.set_param("entreprise_ville", "Alger")
    db.set_param("entreprise_adresse", "Cit\u00e9 des Palmiers, Bab Ezzouar, Alger")
    db.set_param("entreprise_rib", "CCP 0021458 cl\u00e9 47")
    db.set_param("onboarding_fait", "1")

    clients = [
        ("Belkacem Amine", "0661 45 78 21", "Dar El Be\u00efda", "Villa 12, lotissement Es-Sa\u00e2da"),
        ("Ha\u00efdra Nadia", "0770 12 09 33", "Hydra", "R\u00e9sidence Les Oliviers, bloc B"),
        ("Soci\u00e9t\u00e9 EL BARAKA", "0555 90 11 02", "Rouiba", "Zone industrielle, lot 7"),
        ("Mekki Youcef", "0699 33 44 55", "Bab Ezzouar", "Cit\u00e9 AADL, b\u00e2t. 4"),
    ]
    ids_clients = []
    for nom, tel, ville, adresse in clients:
        db.run("INSERT INTO clients (nom,telephone,ville,adresse,date_creation) VALUES (?,?,?,?,?)",
               (nom, tel, ville, adresse, jour(-60)))
        ids_clients.append(db.scalar("SELECT id FROM clients WHERE nom=?", (nom,)))

    chantiers = [
        ("Villa Dar El Be\u00efda \u2014 Peinture", 0, "Peinture", "En cours"),
        ("Appartement Hydra \u2014 Salle de bain", 1, "Plomberie", "En cours"),
        ("D\u00e9p\u00f4t Rouiba \u2014 \u00c9tanch\u00e9it\u00e9", 2, "\u00c9tanch\u00e9it\u00e9", "En cours"),
        ("AADL Bab Ezzouar \u2014 Pl\u00e2tre", 3, "Pl\u00e2tre / Placo", "Termin\u00e9"),
    ]
    ids_chantiers = []
    for nom, index_client, type_travaux, statut in chantiers:
        db.run("INSERT INTO chantiers (nom,client_id,type_travaux,statut,date_debut) "
               "VALUES (?,?,?,?,?)",
               (nom, ids_clients[index_client], type_travaux, statut, jour(-30)))
        ids_chantiers.append(db.scalar("SELECT id FROM chantiers WHERE nom=?", (nom,)))

    plan = [
        ("Peinture", 0, 0, "Facture", "Facture", -22, 180000),
        ("Salle de bain compl\u00e8te", 1, 1, "Facture", "Envoye", -12, 0),
        ("\u00c9tanch\u00e9it\u00e9 terrasse", 2, 2, "Devis", "Envoye", -4, 0),
        ("Pl\u00e2tre / Placo", 3, 3, "Recu", "Paye", -35, None),
    ]
    for modele, index_client, index_chantier, type_doc, statut, decalage, paiement in plan:
        lignes = catalog.postes_template(modele)
        doc_id = docs.creer_document(ids_clients[index_client], ids_chantiers[index_chantier],
                                     type_doc, lignes)
        db.run("UPDATE devis_factures SET date_doc=?, statut=? WHERE id=?",
               (jour(decalage), statut, doc_id))
        total = db.scalar("SELECT total FROM devis_factures WHERE id=?", (doc_id,)) or 0
        if paiement is None:
            docs.enregistrer_paiement(doc_id, float(total), "Esp\u00e8ces", quand=jour(decalage + 3))
        elif paiement:
            docs.enregistrer_paiement(doc_id, float(paiement), "Versement CCP / BaridiMob",
                                      quand=jour(decalage + 2))

    depenses = [
        (0, "Peinture blanche 20 L", 6, "U", 4200),
        (0, "Enduit de lissage", 12, "Sac", 950),
        (1, "Fa\u00efence 30\u00d760", 28, "m2", 1350),
        (1, "Robinetterie mitigeur", 2, "U", 8500),
        (2, "Rouleaux bitume", 14, "U", 3800),
        (3, "Sacs de pl\u00e2tre 40 kg", 40, "Sac", 620),
    ]
    for index_chantier, libelle, qte, unite, pu in depenses:
        db.run("INSERT INTO depenses_materiaux "
               "(chantier_id,libelle,quantite,unite,prix_unitaire,montant,fournisseur,date_achat) "
               "VALUES (?,?,?,?,?,?,?,?)",
               (ids_chantiers[index_chantier], libelle, qte, unite, pu, qte * pu,
                "D\u00e9p\u00f4t El Harrach", jour(-15)))

    equipe = [("Karim (ma\u00e7on)", 4000), ("Sofiane (manoeuvre)", 2500), ("Rachid (t\u00e2cheron)", 5000)]
    for nom, tarif in equipe:
        db.run("INSERT OR IGNORE INTO ouvriers (nom,tarif_jour) VALUES (?,?)", (nom, tarif))

    paies = [
        (0, "Karim (ma\u00e7on)", "Journ\u00e9e", 6, 4000),
        (0, "Sofiane (manoeuvre)", "Journ\u00e9e", 6, 2500),
        (1, "Rachid (t\u00e2cheron)", "Forfait", 0, 45000),
        (2, "Karim (ma\u00e7on)", "Avance", 0, 15000),
    ]
    for index_chantier, nom, type_paie, jours, montant_ou_tarif in paies:
        montant = jours * montant_ou_tarif if type_paie == "Journ\u00e9e" else montant_ou_tarif
        tarif = montant_ou_tarif if type_paie == "Journ\u00e9e" else 0
        db.run("INSERT INTO paie_main_oeuvre "
               "(chantier_id,ouvrier,type_paie,nb_jours,tarif_jour,montant,date_paie) "
               "VALUES (?,?,?,?,?,?,?)",
               (ids_chantiers[index_chantier], nom, type_paie, jours, tarif, montant, jour(-10)))

    print("Donn\u00e9es de d\u00e9monstration cr\u00e9\u00e9es dans %s" % db.DB_PATH)


if __name__ == "__main__":
    main()
