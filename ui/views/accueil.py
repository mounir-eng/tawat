# -*- coding: utf-8 -*-
"""\u00c9cran d'accueil : salutation, bandeau KPI, tuiles d'actions, chantiers en cours.

Libell\u00e9s : arabe d'abord, fran\u00e7ais entre parenth\u00e8ses ; termes techniques en fran\u00e7ais.
"""
import streamlit as st

from core import db
from core.docs import documents
from core.fmt import date_du_jour_fr, dz, nombre
from core.metier import (documents_avec_reste, kpis_mois, rentabilite)
from .. import components as c
from ..theme import JETONS
from . import _communs as k


def afficher():
    entreprise = db.get_param("entreprise_nom") or "Artisan DZ Pro"
    actifs = db.q("SELECT * FROM chantiers WHERE statut='En cours' ORDER BY id DESC")
    impayes = documents_avec_reste()
    kpi = kpis_mois()
    reste_a_facturer = db.scalar(
        "SELECT COALESCE(SUM(total),0) FROM devis_factures WHERE statut='Accepte'") or 0

    # ------------------------------------------------------ salutation
    c.salutation(entreprise, nb_alertes=len(impayes))
    st.markdown('<div class="sm muted" style="margin:-8px 0 10px 2px">%s \u00b7 %s</div>'
                % (date_du_jour_fr(),
                   c.bi("%d \u0648\u0631\u0634\u0627\u062a \u062c\u0627\u0631\u064a\u0629" % len(actifs),
                        "%d chantier(s) en cours" % len(actifs))),
                unsafe_allow_html=True)

    # ------------------------------------------------------ bandeau KPI
    if impayes:
        alerte = {"icone": "\u23f3", "accent": True,
                  "label": c.bi("%d \u0641\u0627\u062a\u0648\u0631\u0629 \u0645\u0639\u0644\u0642\u0629" % len(impayes),
                                "en attente"),
                  "valeur": nombre(kpi["kredi"]), "unite": "DZD",
                  "sous": c.bi("\u0627\u0644\u0645\u062c\u0645\u0648\u0639 \u0627\u0644\u0645\u062a\u0628\u0642\u064a", "Kredi total"),
                  "lien": c.bi("\u0627\u0646\u062a\u0642\u0644 \u0625\u0644\u0649 \u0627\u0644\u0643\u0631\u064a\u062f\u064a", "Voir le Kredi")}
    else:
        alerte = {"icone": "\u2705", "accent": False,
                  "label": c.bi("\u0645\u0627 \u0643\u0627\u064a\u0646 \u062d\u062a\u0649 \u0641\u0627\u062a\u0648\u0631\u0629 \u0645\u0639\u0644\u0642\u0629",
                                "aucune facture en attente"),
                  "valeur": "0", "unite": "DZD",
                  "sous": c.bi("\u0643\u0644 \u0627\u0644\u0632\u0628\u0627\u0626\u0646 \u062e\u0644\u0635\u0648", "tous les clients sont \u00e0 jour")}
    c.bande_kpi([
        {"icone": "\U0001f9fe",
         "label": c.bi("\u0627\u0644\u0628\u0627\u0642\u064a \u0644\u0644\u062a\u0641\u0648\u062a\u0631\u0629", "Reste \u00e0 facturer"),
         "valeur": nombre(reste_a_facturer), "unite": "DZD",
         "sous": c.bi("\u0639\u0631\u0648\u0636 \u0645\u0642\u0628\u0648\u0644\u0629", "devis accept\u00e9s")},
        {"icone": "\U0001f4c8",
         "label": c.bi("\u0645\u062f\u0627\u062e\u064a\u0644 \u0627\u0644\u0634\u0647\u0631", "CA du mois"),
         "valeur": nombre(kpi["encaisse"]), "unite": "DZD",
         "sous": c.bi("\u0645\u0628\u0627\u0644\u063a \u0645\u062d\u0635\u0651\u0644\u0629", "montants encaiss\u00e9s")},
        alerte,
    ])

    # ------------------------------------------------------ tuiles d'actions
    c.section(c.bi("\u0645\u0627\u0630\u0627 \u062a\u0631\u064a\u062f \u0623\u0646 \u062a\u0641\u0639\u0644\u061f", "Actions rapides"))
    c.tuiles([
        ("\U0001f4dd", c.bi("\u0639\u0631\u0636 \u0633\u0639\u0631", "Devis"),
         lambda: k.aller("devis", ouvrir_dialog_devis=True)),
        ("\U0001f3d7\ufe0f", c.bi("\u0648\u0631\u0634\u0629", "Chantier"),
         lambda: k.aller("chantiers")),
        ("\U0001f4b0", c.bi("\u062a\u062d\u0635\u064a\u0644", "Encaisser"),
         lambda: k.aller("kredi")),
        ("\U0001f477", c.bi("\u0639\u0627\u0645\u0644", "Pointer"),
         lambda: k.aller("chantiers")),
        ("\U0001f465", c.bi("\u0632\u0628\u0648\u0646", "Client"),
         lambda: k.aller("clients", dialog_client=True)),
        ("\U0001f9ee", c.bi("\u062d\u0627\u0633\u0628\u0629", "Calculateur"),
         lambda: k.aller("calculs")),
        ("\U0001f4da", c.bi("\u0645\u0643\u062a\u0628\u0629 \u0627\u0644\u0623\u0633\u0639\u0627\u0631", "Prix"),
         lambda: k.aller("prix")),
    ])

    # ------------------------------------------------------ chantiers en cours
    c.section(c.bi("\u0627\u0644\u0648\u0631\u0634\u0627\u062a \u0627\u0644\u062c\u0627\u0631\u064a\u0629", "Chantiers en cours"),
              lien=c.bi("\u0639\u0631\u0636 \u0627\u0644\u0643\u0644", "Tout voir") if len(actifs) > 2 else "")
    if not actifs:
        c.vide("\U0001f3d7\ufe0f",
               c.bi("\u0645\u0627 \u0643\u0627\u064a\u0646 \u062d\u062a\u0649 \u0648\u0631\u0634\u0629", "Aucun chantier en cours"),
               c.bi("\u0623\u0646\u0634\u0626 \u0648\u0631\u0634\u0629 \u0644\u062a\u062a\u0628\u0639 \u0627\u0644\u0645\u0648\u0627\u062f \u0648\u0627\u0644\u0639\u0645\u0627\u0644 \u0648\u0627\u0644\u0631\u0628\u062d",
                    "Cr\u00e9ez un chantier pour suivre mat\u00e9riaux, ouvriers et b\u00e9n\u00e9fice."))
    for chantier in actifs[:3]:
        r = rentabilite(chantier["id"])
        avancement = (r["encaisse"] / r["facture"] * 100) if r["facture"] else 0
        with st.container(border=True):
            haut1, haut2 = st.columns([3, 1])
            haut1.markdown('<div class="nm">%s</div><div class="ds">%s</div>'
                           % (c.e(chantier["nom"]),
                              c.e(chantier.get("client") or chantier.get("type_travaux") or "")),
                           unsafe_allow_html=True)
            haut2.markdown('<div style="text-align:right">%s</div>'
                           % c.pilule(c.bi("\u062c\u0627\u0631\u064a\u0629", "En cours"), "green"),
                           unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])
            col1.markdown('<div class="sm muted" style="margin-top:4px">%s</div>'
                          % c.bi("\u0646\u0633\u0628\u0629 \u0627\u0644\u062a\u062d\u0635\u064a\u0644", "Avancement"),
                          unsafe_allow_html=True)
            col2.markdown('<div class="sm" style="text-align:right;font-weight:700">%s %%</div>'
                          % nombre(avancement), unsafe_allow_html=True)
            c.barre_progression(avancement)
            c.stats3([
                (c.bi("\u0627\u0644\u0645\u064f\u0641\u0648\u062a\u0631", "Factur\u00e9"),
                 "%s DZD" % nombre(r["facture"])),
                (c.bi("\u0627\u0644\u0645\u062d\u0635\u0651\u0644", "Encaiss\u00e9"),
                 "%s DZD" % nombre(r["encaisse"])),
                (c.bi("\u0627\u0644\u0628\u0627\u0642\u064a", "Reste"),
                 "%s DZD" % nombre(r["reste_client"])),
            ])
            if st.button(c.bi("\u0641\u062a\u062d \u0627\u0644\u0648\u0631\u0634\u0629", "Voir le chantier") + "  \u2190",
                         key="acc_ch_%d" % chantier["id"], use_container_width=True):
                k.ouvrir_chantier(chantier["id"])

    # ------------------------------------------------------ relances
    if impayes:
        c.section(c.bi("\u0644\u0644\u062a\u0630\u0643\u064a\u0631", "\u00c0 relancer"))
        for doc in impayes[:3]:
            with st.container(border=True):
                c.carte_contact(
                    doc.get("client") or "Client",
                    "%s \u00b7 %s" % (doc["numero"],
                                      c.bi("%d \u064a\u0648\u0645 \u062a\u0623\u062e\u064a\u0631" % doc["retard"],
                                           "%d jours de retard" % doc["retard"])
                                      if doc["retard"] > 0 else c.bi("\u0642\u064a\u062f \u0627\u0644\u062a\u062d\u0635\u064a\u0644", "en cours")),
                    doc["reste"], "red" if doc["retard"] > 7 else "amber",
                    c.bi("\u0628\u0627\u0642\u064a", "reste"))
                if st.button(c.bi("\u062a\u062d\u0636\u064a\u0631 \u0627\u0644\u062a\u0630\u0643\u064a\u0631", "Pr\u00e9parer la relance"),
                             key="acc_rel_%d" % doc["id"], use_container_width=True):
                    k.aller("kredi", kredi_doc=doc["id"])

    # ------------------------------------------------------ derniers documents
    recents = documents(limite=3)
    if recents:
        c.section(c.bi("\u0622\u062e\u0631 \u0627\u0644\u0648\u062b\u0627\u0626\u0642", "Derniers documents"))
        for doc in recents:
            with st.container(border=True):
                c.carte_document(doc)
                if st.button(c.bi("\u0641\u062a\u062d", "Ouvrir"), key="acc_doc_%d" % doc["id"],
                             use_container_width=True):
                    k.ouvrir_document(doc["id"])
    elif not actifs:
        c.vide("\u2728", c.bi("\u0645\u0631\u062d\u0628\u0627 \u0628\u0643", "Bienvenue"),
               c.bi("\u0627\u0628\u062f\u0623 \u0628\u0639\u0631\u0636 \u0633\u0639\u0631 : \u0627\u062e\u062a\u0631 \u0646\u0645\u0648\u0630\u062c \u0645\u0647\u0646\u062a\u0643 \u0648\u0643\u0644\u0634 \u0645\u062d\u0636\u0631",
                    "Commencez par un devis : choisissez un mod\u00e8le m\u00e9tier, tout est pr\u00e9-rempli."))
