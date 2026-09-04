# -*- coding: utf-8 -*-
"""\u00c9cran Chantiers : d\u00e9penses mat\u00e9riaux, main d'\u0153uvre et rentabilit\u00e9 en direct.

Mode chantier : gros boutons, montants rapides, saisie d'une d\u00e9pense en 3 gestes.
"""
from datetime import date

import streamlit as st

from core import db
from core.docs import documents
from core.fmt import date_fr, dz, nombre
from core.metier import TYPES_TRAVAUX, rentabilite
from .. import components as c
from ..theme import JETONS
from . import _communs as k

STATUTS = ["En cours", "Termin\u00e9", "En pause", "Annul\u00e9"]
TYPES_PAIE = ["Journ\u00e9e", "Avance", "Forfait", "T\u00e2cheron"]


def afficher():
    if st.session_state.get("chantier_ouvert"):
        _detail(st.session_state["chantier_ouvert"])
    else:
        _liste()


def _liste():
    liste = k.chantiers()
    c.entete(c.bi("\u0627\u0644\u0648\u0631\u0634\u0627\u062a", "Chantiers"), "%d chantier(s)" % len(liste))

    if st.button(c.bi("\uff0b  \u0648\u0631\u0634\u0629 \u062c\u062f\u064a\u062f\u0629", "Nouveau chantier"),
                 type="primary", use_container_width=True):
        st.session_state["dialog_chantier"] = True
    if st.session_state.get("dialog_chantier"):
        _dialog_chantier()

    filtre = c.pilules_filtre("Statut", ["En cours", "Tous", "Termin\u00e9"], "filtre_chantier", "En cours")
    if filtre != "Tous":
        liste = [x for x in liste if x["statut"] == filtre]

    if not liste:
        c.vide("\U0001f3d7\ufe0f", "Aucun chantier",
               "Un chantier permet de comparer ce que vous encaissez et ce que vous d\u00e9pensez.")
        return

    for chantier in liste:
        r = rentabilite(chantier["id"])
        cible = db.get_param_num("marge_cible", 30)
        couleur = "green" if r["marge"] >= cible else ("amber" if r["benefice"] >= 0 else "red")
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            col1.markdown('<div class="nm">%s</div><div class="ds">%s \u00b7 %s</div>'
                          % (c.e(chantier["nom"]), c.e(chantier.get("client") or "Sans client"),
                             c.e(chantier.get("type_travaux") or "")), unsafe_allow_html=True)
            col2.markdown('<div style="text-align:right">%s</div>'
                          % c.pilule("%s %%" % nombre(r["marge"]), couleur), unsafe_allow_html=True)
            c.barre_repartition([("Mat\u00e9riaux", r["materiaux"], JETONS["ambre"]),
                                 ("Ouvriers", r["main_oeuvre"], "#8C8880"),
                                 ("B\u00e9n\u00e9fice", max(0.0, r["benefice"]), JETONS["vert"])])
            if st.button("Ouvrir", key="ch_%d" % chantier["id"], use_container_width=True):
                k.ouvrir_chantier(chantier["id"])


@c.dialogue(c.bi("\u0648\u0631\u0634\u0629 \u062c\u062f\u064a\u062f\u0629", "Nouveau chantier"))
def _dialog_chantier():
    client_id = k.selecteur_client("Client", "nc_client",
                                   valeur=(k.selection_differee("nc_client")
                                           if hasattr(k, "selection_differee") else None))
    with st.expander("\uff0b Cr\u00e9er le client"):
        nouveau = k.formulaire_client_rapide("nc")
        if nouveau:
            st.session_state["pre_nc_client"] = nouveau
            st.rerun()
    chantier_id = k.formulaire_chantier_rapide(client_id, "nc_ch")
    if chantier_id:
        st.session_state["dialog_chantier"] = False
        k.ouvrir_chantier(chantier_id)
    if st.button("Fermer", use_container_width=True):
        st.session_state["dialog_chantier"] = False
        st.rerun()


def _detail(chantier_id):
    chantier = db.one("SELECT ch.*, c.nom AS client, c.telephone AS tel FROM chantiers ch "
                      "LEFT JOIN clients c ON c.id=ch.client_id WHERE ch.id=?", (chantier_id,))
    if not chantier:
        st.session_state.pop("chantier_ouvert", None)
        st.rerun()

    r = rentabilite(chantier_id)
    haut1, haut2 = st.columns([3, 1])
    with haut1:
        c.entete(chantier["nom"], "%s \u00b7 %s" % (chantier.get("client") or "Sans client",
                                                    chantier.get("type_travaux") or ""),
                 c.pilule(chantier["statut"], "green" if chantier["statut"] == "En cours" else "grey"))
    if haut2.button("\u2715  Fermer", use_container_width=True):
        st.session_state.pop("chantier_ouvert", None)
        st.rerun()

    c.hero(c.bi("\u0627\u0644\u0631\u0628\u062d \u0627\u0644\u0635\u0627\u0641\u064a \u0644\u0644\u0648\u0631\u0634\u0629", "B\u00e9n\u00e9fice net"),
           nombre(r["benefice"]), "DZD", cases=[
        ("Encaiss\u00e9", nombre(r["encaisse"]), "#8FE3B4"),
        ("D\u00e9pens\u00e9", nombre(r["depenses"]), "#FFD8B4"),
        ("Reste client", nombre(r["reste_client"]), "#FFB4AC"),
    ])
    with st.container(border=True):
        c.barre_repartition([("Mat\u00e9riaux", r["materiaux"], JETONS["ambre"]),
                             ("Ouvriers", r["main_oeuvre"], "#8C8880"),
                             ("B\u00e9n\u00e9fice", max(0.0, r["benefice"]), JETONS["vert"])])
        st.caption("Marge : %s %% \u00b7 objectif %s %%"
                   % (nombre(r["marge"]), nombre(db.get_param_num("marge_cible", 30))))

    onglets = st.tabs(["\U0001f9fe D\u00e9penses", "\U0001f477 Main d'\u0153uvre",
                       "\U0001f4c4 Documents", "\u2699\ufe0f Fiche"])

    # ------------------------------------------------------------- depenses
    with onglets[0]:
        with st.container(border=True):
            st.markdown('<div class="sec" style="margin-top:0">Ajouter un achat</div>',
                        unsafe_allow_html=True)
            libelle = st.text_input("Achat", key="dep_lib", label_visibility="collapsed",
                                    placeholder="Sacs de ciment, pot de peinture, taxi\u2026")
            col1, col2, col3 = st.columns([1, 1, 1.2])
            qte = col1.number_input("Qt\u00e9", min_value=0.0, value=1.0, step=1.0, key="dep_qte")
            unite = col2.selectbox("Unit\u00e9", ["U", "Sac", "Kg", "L", "m2", "m3", "Lot"], key="dep_uni")
            pu = col3.number_input("Prix unitaire", min_value=0.0, value=0.0, step=100.0, key="dep_pu")
            col4, col5 = st.columns(2)
            fournisseur = col4.text_input("Fournisseur", key="dep_four", placeholder="D\u00e9p\u00f4t\u2026")
            quand = col5.date_input("Date", value=date.today(), key="dep_date", format="DD/MM/YYYY")
            st.caption("Total : %s" % dz(qte * pu))
            if st.button("Enregistrer la d\u00e9pense", type="primary", use_container_width=True,
                         disabled=not libelle.strip() or qte * pu <= 0):
                db.run("INSERT INTO depenses_materiaux "
                       "(chantier_id,libelle,quantite,unite,prix_unitaire,montant,fournisseur,date_achat) "
                       "VALUES (?,?,?,?,?,?,?,?)",
                       (chantier_id, libelle.strip(), qte, unite, pu, qte * pu,
                        fournisseur.strip(), quand.isoformat()))
                c.toast("D\u00e9pense ajout\u00e9e : %s" % dz(qte * pu))
                st.rerun()

        depenses = db.q("SELECT * FROM depenses_materiaux WHERE chantier_id=? "
                        "ORDER BY date(date_achat) DESC, id DESC", (chantier_id,))
        if not depenses:
            c.vide("\U0001f9fe", "Aucune d\u00e9pense", "Notez chaque achat : la marge reste juste.")
        for d in depenses:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.markdown('<div class="nm">%s</div><div class="ds">%s \u00b7 %s %s \u00d7 %s</div>'
                              % (c.e(d["libelle"]), date_fr(d["date_achat"]), nombre(d["quantite"]),
                                 c.e(d["unite"]), nombre(d["prix_unitaire"])), unsafe_allow_html=True)
                col2.markdown('<div style="text-align:right" class="money">%s</div>'
                              % nombre(d["montant"]), unsafe_allow_html=True)
                if st.button("Supprimer", key="sdep_%d" % d["id"], use_container_width=True):
                    db.run("DELETE FROM depenses_materiaux WHERE id=?", (d["id"],))
                    st.rerun()

    # ------------------------------------------------------------- main d'oeuvre
    with onglets[1]:
        with st.container(border=True):
            st.markdown('<div class="sec" style="margin-top:0">Pointer une journ\u00e9e / une avance</div>',
                        unsafe_allow_html=True)
            ouvriers = [o["nom"] for o in db.q("SELECT nom FROM ouvriers ORDER BY nom")]
            col1, col2 = st.columns([1.4, 1])
            if ouvriers:
                choix = col1.selectbox("Ouvrier", ouvriers + ["\uff0b Nouvel ouvrier"], key="mo_sel")
                nom = col1.text_input("Nom", key="mo_nom") if choix == "\uff0b Nouvel ouvrier" else choix
            else:
                nom = col1.text_input("Ouvrier", key="mo_nom", placeholder="Nom du ma\u00e7on / manoeuvre")
            type_paie = col2.selectbox("Type", TYPES_PAIE, key="mo_type")
            col3, col4 = st.columns(2)
            if type_paie == "Journ\u00e9e":
                jours = col3.number_input("Nombre de journ\u00e9es", min_value=0.0, value=1.0, step=0.5,
                                          key="mo_j")
                tarif = col4.number_input("Tarif / jour", min_value=0.0,
                                          value=db.get_param_num("tarif_jour_defaut", 3000),
                                          step=500.0, key="mo_t")
                montant = jours * tarif
            else:
                jours, tarif = 0.0, 0.0
                montant = col3.number_input("Montant vers\u00e9", min_value=0.0, value=0.0, step=500.0,
                                            key="mo_m")
                col4.caption("Avances et forfaits sont d\u00e9duits du b\u00e9n\u00e9fice du chantier.")
            quand = st.date_input("Date", value=date.today(), key="mo_date", format="DD/MM/YYYY")
            st.caption("Total : %s" % dz(montant))
            if st.button("Enregistrer", type="primary", use_container_width=True,
                         disabled=not (nom or "").strip() or montant <= 0):
                db.run("INSERT OR IGNORE INTO ouvriers (nom,tarif_jour) VALUES (?,?)",
                       (nom.strip(), tarif))
                db.run("INSERT INTO paie_main_oeuvre "
                       "(chantier_id,ouvrier,type_paie,nb_jours,tarif_jour,montant,date_paie) "
                       "VALUES (?,?,?,?,?,?,?)",
                       (chantier_id, nom.strip(), type_paie, jours, tarif, montant, quand.isoformat()))
                c.toast("Pointage enregistr\u00e9")
                st.rerun()

        paies = db.q("SELECT * FROM paie_main_oeuvre WHERE chantier_id=? "
                     "ORDER BY date(date_paie) DESC, id DESC", (chantier_id,))
        if not paies:
            c.vide("\U0001f477", "Aucun pointage", "Journ\u00e9es, avances et t\u00e2cherons se notent ici.")
        for p in paies:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                detail = ("%s journ\u00e9e(s) \u00d7 %s" % (nombre(p["nb_jours"]), nombre(p["tarif_jour"]))
                          if p["type_paie"] == "Journ\u00e9e" else p["type_paie"])
                col1.markdown('<div class="nm">%s</div><div class="ds">%s \u00b7 %s</div>'
                              % (c.e(p["ouvrier"]), date_fr(p["date_paie"]), c.e(detail)),
                              unsafe_allow_html=True)
                col2.markdown('<div style="text-align:right" class="money">%s</div>'
                              % nombre(p["montant"]), unsafe_allow_html=True)
                if st.button("Supprimer", key="smo_%d" % p["id"], use_container_width=True):
                    db.run("DELETE FROM paie_main_oeuvre WHERE id=?", (p["id"],))
                    st.rerun()

    # ------------------------------------------------------------- documents
    with onglets[2]:
        liste = [d for d in documents() if d.get("chantier_id") == chantier_id]
        if not liste:
            c.vide("\U0001f4c4", "Aucun document li\u00e9",
                   "Cr\u00e9ez un devis et rattachez-le \u00e0 ce chantier.")
        for doc in liste:
            with st.container(border=True):
                c.carte_document(doc)
                if st.button("Ouvrir", key="chdoc_%d" % doc["id"], use_container_width=True):
                    k.ouvrir_document(doc["id"])

    # ------------------------------------------------------------- fiche
    with onglets[3]:
        with st.container(border=True):
            nom = st.text_input("Nom du chantier", value=chantier["nom"], key="fch_nom")
            col1, col2 = st.columns(2)
            type_travaux = col1.selectbox("Type de travaux", TYPES_TRAVAUX,
                                          index=TYPES_TRAVAUX.index(chantier["type_travaux"])
                                          if chantier.get("type_travaux") in TYPES_TRAVAUX else 0,
                                          key="fch_type")
            statut = col2.selectbox("Statut", STATUTS,
                                    index=STATUTS.index(chantier["statut"])
                                    if chantier.get("statut") in STATUTS else 0, key="fch_statut")
            adresse = st.text_input("Adresse", value=chantier.get("adresse") or "", key="fch_adr")
            note = st.text_area("Notes de chantier", value=chantier.get("note") or "", key="fch_note")
            if st.button("Enregistrer la fiche", type="primary", use_container_width=True):
                db.run("UPDATE chantiers SET nom=?, type_travaux=?, statut=?, adresse=?, note=? WHERE id=?",
                       (nom, type_travaux, statut, adresse, note, chantier_id))
                c.toast("Fiche mise \u00e0 jour")
                st.rerun()
            if st.button("\U0001f5d1\ufe0f Supprimer le chantier", use_container_width=True):
                db.run("DELETE FROM chantiers WHERE id=?", (chantier_id,))
                st.session_state.pop("chantier_ouvert", None)
                st.rerun()
