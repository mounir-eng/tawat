# -*- coding: utf-8 -*-
"""\u0645\u0643\u062a\u0628\u0629 \u0627\u0644\u0623\u0633\u0639\u0627\u0631 : biblioth\u00e8que de prix \u00e9ditable.

Chaque prestation : prix modifiable en un tap, suppression, ajout rapide.
Le prix modifi\u00e9 est celui propos\u00e9 dans les prochains devis.
"""
from datetime import date

import streamlit as st

from core import catalog, db
from core.metier import UNITES
from .. import components as c


def afficher():
    rows = catalog.bibliotheque("", 300)
    c.entete(c.bi("\u0645\u0643\u062a\u0628\u0629 \u0627\u0644\u0623\u0633\u0639\u0627\u0631", "Biblioth\u00e8que de prix"),
             c.bi("%d \u062e\u062f\u0645\u0629 \u00b7 \u0627\u0644\u0633\u0639\u0631 \u0627\u0644\u0645\u0639\u062f\u0651\u0644 \u064a\u064f\u0642\u062a\u0631\u062d \u0641\u064a \u0627\u0644\u0640 Devis \u0627\u0644\u0642\u0627\u062f\u0645\u0629",
                  "%d prestations \u00b7 le prix modifi\u00e9 est propos\u00e9 dans les prochains devis",
                  len(rows)))

    # ------------------------------------------------------ ajout rapide
    with st.container(border=True):
        st.markdown('<div class="sec" style="margin-top:0">%s</div>'
                    % c.bi("\uff0b \u062e\u062f\u0645\u0629 \u062c\u062f\u064a\u062f\u0629", "Nouvelle prestation"),
                    unsafe_allow_html=True)
        libelle = st.text_input(c.bi("\u0627\u0644\u062a\u0639\u064a\u064a\u0646", "D\u00e9signation"), key="pl_lib",
                                placeholder="Interrupteur simple, Lampe / Point lumineux\u2026")
        col1, col2, col3 = st.columns(3)
        unite = col1.selectbox(c.bi("\u0627\u0644\u0648\u062d\u062f\u0629", "Unit\u00e9"), UNITES, key="pl_uni")
        prix = col2.number_input(c.bi("\u0627\u0644\u0633\u0639\u0631", "Prix") + " (DZD)",
                                 min_value=0.0, step=100.0, key="pl_prix")
        metier = col3.selectbox(c.bi("\u0627\u0644\u0645\u064a\u062f\u0627\u0646", "M\u00e9tier"),
                                list(catalog.TEMPLATES.keys()), key="pl_metier")
        if st.button(c.bi("\u0623\u0636\u0641 \u0625\u0644\u0649 \u0627\u0644\u0645\u0643\u062a\u0628\u0629", "Ajouter \u00e0 la biblioth\u00e8que"),
                     type="primary", use_container_width=True,
                     disabled=not libelle.strip() or prix <= 0):
            db.run("INSERT INTO catalogue "
                   "(libelle, metier, unite, prix_unitaire, cout_materiaux, cout_pose, usages, dernier_usage) "
                   "VALUES (?,?,?,?,0,0,1,?) "
                   "ON CONFLICT(libelle, unite) DO UPDATE SET "
                   "prix_unitaire=excluded.prix_unitaire, metier=excluded.metier",
                   (libelle.strip(), metier, unite, float(prix), date.today().isoformat()))
            c.toast(c.bi("\u2713 \u0623\u0636\u064a\u0641\u062a / \u062d\u064f\u062f\u0651\u062b\u062a", "Prestation enregistr\u00e9e"))
            st.rerun()

    if not rows:
        c.vide("\U0001f4da", c.bi("\u0627\u0644\u0645\u0643\u062a\u0628\u0629 \u0641\u0627\u0631\u063a\u0629", "Biblioth\u00e8que vide"),
               c.bi("\u0623\u0636\u0641 \u062e\u062f\u0645\u0629 \u0641\u0648\u0642\u060c \u0623\u0648 \u062d\u0645\u0651\u0644 \u0645\u0643\u062a\u0628\u0629 \u0645\u0647\u0646\u062a\u0643 \u0645\u0646 \u0627\u0644\u0625\u0639\u062f\u0627\u062f\u0627\u062a",
                    "Ajoutez une prestation ou rechargez la biblioth\u00e8que m\u00e9tier depuis R\u00e9glages."))
        return

    # ------------------------------------------------------ recherche + filtre m\u00e9tier
    recherche = st.text_input(c.bi("\u0628\u062d\u062b", "Rechercher"), key="pl_rech",
                              label_visibility="collapsed",
                              placeholder="\U0001f50e " + c.bi("\u0627\u0628\u062d\u062b \u0639\u0646 \u062e\u062f\u0645\u0629\u2026",
                                                               "Rechercher une prestation\u2026"))
    if recherche:
        rows = [r for r in rows if recherche.lower() in (r["libelle"] or "").lower()]

    label_tous = c.bi("\u0627\u0644\u0643\u0644", "Tous")
    metiers = sorted({(r["metier"] or "Autre") for r in rows})
    filtre = c.pilules_filtre("M\u00e9tier", [label_tous] + metiers, "pl_filtre", label_tous)
    if filtre != label_tous:
        rows = [r for r in rows if (r["metier"] or "Autre") == filtre]

    # ------------------------------------------------------ liste \u00e9ditable, group\u00e9e par m\u00e9tier
    par_metier = {}
    for r in rows:
        par_metier.setdefault(r["metier"] or "Autre", []).append(r)
    for metier_nom, groupe in par_metier.items():
        c.section(metier_nom + " \u00b7 %d" % len(groupe))
        for r in groupe:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2.2, 1.2, 0.9])
                col1.markdown('<div class="nm">%s</div><div class="ds">%s \u00b7 %s</div>'
                              % (c.e(r["libelle"]), c.e(r["unite"]),
                                 c.bi("\u0627\u0633\u062a\u064f\u062e\u062f\u0645\u062a %d \u0645\u0631\u0629",
                                      "utilis\u00e9e %d fois", r["usages"] or 0)),
                              unsafe_allow_html=True)
                ancien = float(r["prix_unitaire"] or 0)
                nouveau = col2.number_input(c.bi("\u0627\u0644\u0633\u0639\u0631", "Prix") + " DZD",
                                            min_value=0.0, step=50.0, value=ancien,
                                            key="pl_p_%d" % r["id"], label_visibility="collapsed")
                if nouveau != ancien:
                    db.run("UPDATE catalogue SET prix_unitaire=?, dernier_usage=? WHERE id=?",
                           (float(nouveau), date.today().isoformat(), r["id"]))
                    c.toast(c.bi("\u2713 \u062d\u064f\u062f\u0651\u062b \u0627\u0644\u0633\u0639\u0631", "Prix mis \u00e0 jour"))
                if col3.button("\U0001f5d1\ufe0f", key="pl_del_%d" % r["id"],
                               use_container_width=True):
                    db.run("DELETE FROM catalogue WHERE id=?", (r["id"],))
                    st.rerun()
