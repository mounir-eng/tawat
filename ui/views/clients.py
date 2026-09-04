# -*- coding: utf-8 -*-
"""\u00c9cran Clients : carnet d'adresses avec encours et contact en un tap."""
import streamlit as st

from core import db
from core.docs import documents
from core.fmt import dz, lien_viber, lien_whatsapp, nombre, tel_joli
from core.metier import total_paye
from .. import components as c
from . import _communs as k


def afficher():
    liste = k.clients()
    c.entete(c.bi("\u0627\u0644\u0632\u0628\u0627\u0626\u0646", "Clients"),
             "%d \u0632\u0628\u0648\u0646 \u0641\u064a \u0627\u0644\u062f\u0641\u062a\u0631 (%d client(s))" % (len(liste), len(liste)))

    if st.button(c.bi("\uff0b  \u0632\u0628\u0648\u0646 \u062c\u062f\u064a\u062f", "Nouveau client"),
                 type="primary", use_container_width=True):
        st.session_state["dialog_client"] = True
    if st.session_state.get("dialog_client"):
        _dialog_client()

    recherche = st.text_input("Rechercher", key="rech_client", label_visibility="collapsed",
                              placeholder="\U0001f50e  Rechercher un nom ou un num\u00e9ro\u2026")
    if recherche:
        motif = recherche.lower()
        liste = [x for x in liste
                 if motif in (x["nom"] or "").lower() or motif in (x.get("telephone") or "")]

    if not liste:
        c.vide("\U0001f465", "Aucun client",
               "Ajoutez un client : son num\u00e9ro suffit pour envoyer devis et relances.")
        return

    tous_docs = documents()
    for client in liste:
        docs_client = [d for d in tous_docs if d.get("client_id") == client["id"]]
        encours = sum(max(0.0, float(d.get("total") or 0) - total_paye(d["id"]))
                      for d in docs_client if d["statut"] not in ("Brouillon", "Annule"))
        chiffre = sum(float(d.get("total") or 0) for d in docs_client
                      if d["type_doc"] in ("Facture", "Recu"))
        with st.container(border=True):
            c.carte_contact(client["nom"],
                            "%s \u00b7 %d document(s)" % (tel_joli(client.get("telephone")), len(docs_client)),
                            encours if encours > 1 else chiffre,
                            "red" if encours > 1 else "blue",
                            "reste" if encours > 1 else "factur\u00e9")
            col1, col2, col3 = st.columns(3)
            with col1:
                c.bouton_lien("WhatsApp", lien_whatsapp(client.get("telephone"), ""), "\U0001f4ac",
                              "cwa_%d" % client["id"])
            with col2:
                c.bouton_lien("Viber", lien_viber(client.get("telephone"), ""), "\U0001f4de",
                              "cvi_%d" % client["id"])
            if col3.button("Fiche", key="cfi_%d" % client["id"], use_container_width=True):
                st.session_state["client_ouvert"] = client["id"]
        if st.session_state.get("client_ouvert") == client["id"]:
            _dialog_fiche(client["id"])


@c.dialogue(c.bi("\u0632\u0628\u0648\u0646 \u062c\u062f\u064a\u062f", "Nouveau client"))
def _dialog_client():
    nouveau = k.formulaire_client_rapide("cli")
    if nouveau:
        st.session_state["dialog_client"] = False
        st.rerun()
    if st.button("Fermer", use_container_width=True):
        st.session_state["dialog_client"] = False
        st.rerun()


@c.dialogue(c.bi("\u0645\u0644\u0641 \u0627\u0644\u0632\u0628\u0648\u0646", "Fiche client"))
def _dialog_fiche(client_id):
    client = db.one("SELECT * FROM clients WHERE id=?", (client_id,))
    if not client:
        st.session_state.pop("client_ouvert", None)
        return
    nom = st.text_input("Nom", value=client["nom"], key="fc_nom")
    col1, col2 = st.columns(2)
    tel = col1.text_input("T\u00e9l\u00e9phone", value=client.get("telephone") or "", key="fc_tel")
    ville = col2.text_input("Ville", value=client.get("ville") or "", key="fc_ville")
    adresse = st.text_input("Adresse", value=client.get("adresse") or "", key="fc_adr")
    note = st.text_area("Note (code portail, pr\u00e9f\u00e9rences\u2026)", value=client.get("note") or "",
                        key="fc_note")

    docs_client = [d for d in documents() if d.get("client_id") == client_id]
    if docs_client:
        st.markdown('<div class="sec">Historique</div>', unsafe_allow_html=True)
        for d in docs_client[:6]:
            st.markdown('<div style="display:flex;justify-content:space-between;padding:4px 0">'
                        '<span class="sm">%s \u00b7 %s</span><span class="money sm">%s</span></div>'
                        % (c.e(d["numero"]), c.e(d["type_doc"]), nombre(d["total"])),
                        unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    if b1.button("Enregistrer", type="primary", use_container_width=True):
        db.run("UPDATE clients SET nom=?, telephone=?, ville=?, adresse=?, note=? WHERE id=?",
               (nom, tel, ville, adresse, note, client_id))
        st.session_state.pop("client_ouvert", None)
        c.toast("Fiche enregistr\u00e9e")
        st.rerun()
    if b2.button("Fermer", use_container_width=True):
        st.session_state.pop("client_ouvert", None)
        st.rerun()
