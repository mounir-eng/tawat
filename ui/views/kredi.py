# -*- coding: utf-8 -*-
"""\u00c9cran Kredi : qui doit combien, depuis combien de temps, et relance en un tap."""
import streamlit as st

from core import docs
from core.fmt import date_fr, dz, lien_sms, lien_viber, lien_whatsapp, nombre
from core.metier import (MODES_PAIEMENT, documents_avec_reste, message_relance,
                            ton_relance)
from .. import components as c
from ..theme import JETONS
from . import _communs as k

TONS = {"doux": "Rappel doux", "normal": "Relance normale", "ferme": "Relance ferme"}


def afficher():
    impayes = documents_avec_reste()
    total = sum(d["reste"] for d in impayes)
    c.entete(c.bi("\u0627\u0644\u0643\u0631\u064a\u062f\u064a", "Kredi") + " \u00b7 " + c.bi("\u0641\u0644\u0648\u0633 \u062a\u062d\u0635\u0644\u0647\u0627", "argent \u00e0 rentrer"),
             "%d client(s) concern\u00e9(s)" % len(impayes))

    en_retard = [d for d in impayes if d["retard"] > 0]
    c.hero(c.bi("\u0627\u0644\u0645\u062c\u0645\u0648\u0639 \u0644\u0644\u062a\u062d\u0635\u064a\u0644", "Total \u00e0 encaisser"),
           nombre(total), "DZD", cases=[
        (c.bi("\u0645\u062a\u0623\u062e\u0631", "En retard"), nombre(sum(d["reste"] for d in en_retard)), "#FFB4AC"),
        (c.bi("\u0641\u064a \u0627\u0644\u0622\u062c\u0627\u0644", "Dans les d\u00e9lais"),
         nombre(total - sum(d["reste"] for d in en_retard)), "#8FE3B4"),
    ])

    if not impayes:
        c.vide("\U0001f389", "Aucun kredi en cours", "Tous vos clients sont \u00e0 jour. Bravo !")
        return

    filtre = c.pilules_filtre("Filtre", ["Tous", "En retard", "Gros montants"], "filtre_kredi", "Tous")
    if filtre == "En retard":
        impayes = en_retard
    elif filtre == "Gros montants":
        impayes = sorted(impayes, key=lambda d: -d["reste"])

    for doc in impayes:
        retard = doc["retard"]
        couleur = "red" if retard > 30 else ("amber" if retard > 0 else "blue")
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            col1.markdown('<div class="row">%s<div><div class="nm">%s</div>'
                          '<div class="ds">%s \u00b7 \u00e9ch\u00e9ance %s</div></div></div>'
                          % (c.avatar(doc.get("client") or "?", couleur),
                             c.e(doc.get("client") or "Client"), c.e(doc["numero"]),
                             date_fr(doc.get("echeance") or doc.get("date_doc"))),
                          unsafe_allow_html=True)
            col2.markdown('<div style="text-align:right"><div class="money" style="color:%s">%s</div>'
                          '<div class="xs muted">reste sur %s</div>%s</div>'
                          % (JETONS["rouge"] if retard > 0 else JETONS["texte"],
                             nombre(doc["reste"]), nombre(doc["total"]),
                             c.pilule("%d j de retard" % retard if retard > 0 else "\u00c0 jour", couleur)),
                          unsafe_allow_html=True)

            avancement = (doc["paye"] / doc["total"] * 100) if doc["total"] else 0
            c.barre_repartition([("Vers\u00e9", doc["paye"], JETONS["vert"]),
                                 ("Reste", doc["reste"], JETONS["surface2"])], legende=False)
            st.caption("%s vers\u00e9s \u00b7 %s %% du total" % (dz(doc["paye"]), nombre(avancement)))

            b1, b2 = st.columns(2)
            if b1.button(c.bi("\U0001f4ac \u062a\u0630\u0643\u064a\u0631", "Relancer"),
                         key="rel_%d" % doc["id"], use_container_width=True,
                         type="primary"):
                st.session_state["kredi_doc"] = doc["id"]
                st.rerun()
            if b2.button(c.bi("\U0001f4b5 \u062a\u062d\u0635\u064a\u0644", "Encaisser"),
                         key="enc_%d" % doc["id"], use_container_width=True):
                st.session_state["kredi_enc"] = doc["id"]
                st.rerun()

        if st.session_state.get("kredi_doc") == doc["id"]:
            _dialog_relance(doc)
        if st.session_state.get("kredi_enc") == doc["id"]:
            _dialog_encaissement(doc)


@c.dialogue(c.bi("\u062a\u0630\u0643\u064a\u0631 \u0627\u0644\u0632\u0628\u0648\u0646", "Relance client"))
def _dialog_relance(doc):
    st.markdown('<div class="sm muted">%s \u00b7 %s \u00b7 reste %s</div>'
                % (c.e(doc.get("client") or ""), c.e(doc["numero"]), dz(doc["reste"])),
                unsafe_allow_html=True)

    defaut = TONS[ton_relance(doc["retard"])]
    ton_libelle = c.pilules_filtre("Ton", list(TONS.values()), "ton_relance_%d" % doc["id"], defaut)
    ton = [k_ for k_, v in TONS.items() if v == ton_libelle][0]
    langue_libelle = c.pilules_filtre("Langue", ["Fran\u00e7ais", "Darija (arabe)"],
                                      "langue_relance_%d" % doc["id"], "Fran\u00e7ais")
    langue = "ar" if langue_libelle.startswith("Darija") else "fr"

    texte = message_relance(doc, langue, ton)
    texte = st.text_area("Message", value=texte, height=170, key="txt_rel_%d" % doc["id"])
    st.caption("Le ton s'adapte automatiquement au retard : doux avant 7 jours, "
               "ferme au-del\u00e0 d'un mois.")

    tel = doc.get("tel") or ""
    if not tel:
        st.warning("Num\u00e9ro manquant : ajoutez-le dans la fiche client.")
    col1, col2, col3 = st.columns(3)
    with col1:
        c.bouton_lien("WhatsApp", lien_whatsapp(tel, texte), "\U0001f4ac", "kwa_%d" % doc["id"], "primary")
    with col2:
        c.bouton_lien("Viber", lien_viber(tel, texte), "\U0001f4de", "kvi_%d" % doc["id"])
    with col3:
        c.bouton_lien("SMS", lien_sms(tel, texte), "\u2709\ufe0f", "ksm_%d" % doc["id"])
    if st.button("Fermer", use_container_width=True, key="frel_%d" % doc["id"]):
        st.session_state.pop("kredi_doc", None)
        st.rerun()


@c.dialogue(c.bi("\u062a\u062d\u0635\u064a\u0644 \u062f\u0641\u0639\u0629", "Encaisser un versement"))
def _dialog_encaissement(doc):
    st.markdown('<div class="sm muted">%s \u00b7 reste %s</div>'
                % (c.e(doc.get("client") or ""), dz(doc["reste"])), unsafe_allow_html=True)
    cle = "mnt_enc_%d" % doc["id"]
    st.session_state.setdefault(cle, float(doc["reste"]))
    k.boutons_montants_rapides(cle, (5000, 10000, 20000, int(doc["reste"]) or 1000))
    montant = st.number_input("Montant re\u00e7u", min_value=0.0, step=1000.0, key=cle)
    mode = k.selecteur_mode_paiement("mode_enc_%d" % doc["id"])
    note = st.text_input("Note", key="note_enc_%d" % doc["id"], placeholder="Acompte, solde\u2026")
    if st.button("Valider l'encaissement", type="primary", use_container_width=True,
                 disabled=montant <= 0):
        docs.enregistrer_paiement(doc["id"], montant, mode, note=note)
        st.session_state.pop("kredi_enc", None)
        c.toast("Encaiss\u00e9 : %s" % dz(montant))
        st.rerun()
    if st.button("Fermer", use_container_width=True, key="fenc_%d" % doc["id"]):
        st.session_state.pop("kredi_enc", None)
        st.rerun()
