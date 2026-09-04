# -*- coding: utf-8 -*-
"""الزبائن · Clients : carnet d'adresses en cartes, encours visible, contact en un tap.

Même grammaire visuelle que l'annuaire : filtres mémorisés, grille de cartes
responsives, trois actions par fiche (Appeler, WhatsApp, BaridiMob).
"""
import streamlit as st

from core import db, wilayas
from core.docs import documents
from core.fmt import nombre, tel_joli
from core.metier import total_paye
from .. import cartes, champs, etat
from .. import components as c
from . import _communs as k

ESPACE = "clients"

TRIS = [
    ("nom", "\u0623\u0628\u062c\u062f\u064a - A\u2192Z"),
    ("reste", "\u0627\u0644\u0643\u0631\u064a\u062f\u064a \u0627\u0644\u0623\u0643\u0628\u0631 - Reste \u00e0 payer"),
    ("chiffre", "\u0627\u0644\u0623\u0643\u062b\u0631 \u0634\u0631\u0627\u0621 - Chiffre d'affaires"),
    ("recent", "\u0627\u0644\u0623\u062d\u062f\u062b - R\u00e9cents"),
]
CLE_TRI = {libelle: cle for cle, libelle in TRIS}
DEFAUTS = {"q": "", "wilaya": None, "dette": False, "tri": TRIS[0][1]}


# --------------------------------------------------------------------- ecran
def afficher():
    identifiant = etat.depuis_url(ESPACE)      # ?fiche=7 depuis une carte
    liste = _enrichis()

    total_reste = sum(x["reste"] for x in liste)
    c.entete("\u0627\u0644\u0632\u0628\u0627\u0626\u0646 \u00b7 Clients",
             "Carnet d'adresses, encours et relances polies",
             c.pilule("%d" % len(liste), "blue") if liste else None)

    if liste:
        c.bande_kpi([
            {"icone": "\U0001f91d", "label": "\u0627\u0644\u0632\u0628\u0627\u0626\u0646 / Clients",
             "valeur": nombre(len(liste))},
            {"icone": "\U0001f4b0", "label": "\u0627\u0644\u0643\u0631\u064a\u062f\u064a / Reste \u00e0 payer",
             "valeur": nombre(total_reste), "unite": "DZD",
             "accent": total_reste > 1},
            {"icone": "\U0001f4c4", "label": "\u0627\u0644\u0648\u0631\u0642 / Documents",
             "valeur": nombre(sum(x["nb_docs"] for x in liste))},
        ])

    gauche, droite = st.columns(2)
    if gauche.button("\u2795 \u0632\u0628\u0648\u0646 \u062c\u062f\u064a\u062f  \u00b7  Nouveau client", type="primary",
                     use_container_width=True, key="cl_add"):
        _dialog_client()
    actifs = etat.nb_actifs(ESPACE, DEFAUTS)
    if droite.button("\u267b\ufe0f \u0645\u0633\u062d \u0627\u0644\u0645\u0631\u0634\u062d\u0627\u062a  \u00b7  Effacer les filtres (%d)" % actifs,
                     use_container_width=True, key="cl_reset", disabled=not actifs):
        etat.reinitialiser(ESPACE, DEFAUTS)
        st.rerun()

    _filtres()
    fiches = _filtrer(liste)

    if not fiches:
        if liste:
            c.vide("\U0001f50d", "\u0644\u0627 \u0646\u062a\u064a\u062c\u0629 \u00b7 Aucun r\u00e9sultat",
                   "Changez de wilaya ou effacez les filtres.")
        else:
            c.vide("\U0001f91d", "\u0644\u0627 \u064a\u0648\u062c\u062f \u0632\u0628\u0648\u0646 \u00b7 Aucun client",
                   "Un nom et un num\u00e9ro suffisent pour envoyer devis et relances.")
        return

    cartes.bandeau_resultats(len(fiches), "\u0632\u0628\u0648\u0646", "client(s)", actifs)
    cartes.grille([_en_carte(x) for x in fiches],
                  entreprise=db.get_param("entreprise_nom") or "",
                  rip=db.get_param("entreprise_rip") or "")

    if identifiant:
        _dialog_fiche(identifiant)


def _filtres():
    """Recherche en ligne + tiroir de filtres : aucune colonne laterale."""
    actifs = etat.nb_actifs(ESPACE, DEFAUTS)
    champs.texte("\u0628\u062d\u062b", "Rechercher un nom, un num\u00e9ro, une ville",
                 icone="\U0001f50d", placeholder="Mme Kadri, 0661\u2026",
                 **etat.lie(ESPACE, "q", ""))
    with st.expander("\u2699\ufe0f  \u0645\u0631\u0634\u062d\u0627\u062a \u00b7 Filtres" +
                     (("  (%d)" % actifs) if actifs else ""),
                     expanded=bool(actifs)):
        col1, col2 = st.columns(2)
        with col1:
            champs.choix("\u0627\u0644\u062a\u0631\u062a\u064a\u0628", "Trier par",
                         [t[1] for t in TRIS], icone="\u2195\ufe0f",
                         **etat.lie(ESPACE, "tri", TRIS[0][1]))
        with col2:
            champs.wilaya(**etat.lie(ESPACE, "wilaya", None))
        champs.bascule("\u0639\u0646\u062f\u0647\u0645 \u0643\u0631\u064a\u062f\u064a",
                       "Avec reste \u00e0 payer",
                       **etat.lie(ESPACE, "dette", False))
    cartes.puces_filtres(_puces())


def _puces():
    """Resume des filtres actifs, affiche sous la recherche."""
    puces = []
    code = etat.filtre(ESPACE, "wilaya")
    if code:
        puces.append(("\U0001f4cd " + wilayas.libelle(code, ""), True))
    if etat.filtre(ESPACE, "dette", False):
        puces.append(("\U0001f4b0 \u0643\u0631\u064a\u062f\u064a \u00b7 impay\u00e9s", True))
    tri = etat.filtre(ESPACE, "tri", TRIS[0][1])
    if tri and tri != TRIS[0][1]:
        puces.append(("\u2195\ufe0f " + str(tri), False))
    return puces


# ---------------------------------------------------------------- donnees
def _enrichis():
    """Clients + encours + chiffre d'affaires, calculés une seule fois par run."""
    tous_docs = documents()
    par_client = {}
    for doc in tous_docs:
        par_client.setdefault(doc.get("client_id"), []).append(doc)
    resultat = []
    for client in k.clients():
        docs = par_client.get(client["id"], [])
        reste = sum(max(0.0, float(d.get("total") or 0) - total_paye(d["id"]))
                    for d in docs if d.get("statut") not in ("Brouillon", "Annule"))
        chiffre = sum(float(d.get("total") or 0) for d in docs
                      if d.get("type_doc") in ("Facture", "Recu"))
        fiche = dict(client)
        fiche.update({"reste": reste, "chiffre": chiffre, "nb_docs": len(docs)})
        resultat.append(fiche)
    return resultat


def _filtrer(liste):
    motif = (etat.filtre(ESPACE, "q", "") or "").strip().lower()
    code = etat.filtre(ESPACE, "wilaya")
    dette = bool(etat.filtre(ESPACE, "dette", False))
    tri = CLE_TRI.get(etat.filtre(ESPACE, "tri", TRIS[0][1]), "nom")

    fiches = []
    for x in liste:
        if motif and motif not in " ".join([
                (x.get("nom") or ""), (x.get("telephone") or ""),
                (x.get("ville") or ""), (x.get("adresse") or "")]).lower():
            continue
        if code and int(x.get("wilaya") or 0) != int(code):
            continue
        if dette and x["reste"] <= 1:
            continue
        fiches.append(x)

    if tri == "reste":
        fiches.sort(key=lambda x: -x["reste"])
    elif tri == "chiffre":
        fiches.sort(key=lambda x: -x["chiffre"])
    elif tri == "recent":
        fiches.sort(key=lambda x: -(x.get("id") or 0))
    else:
        fiches.sort(key=lambda x: (x.get("nom") or "").lower())
    return fiches


def _en_carte(fiche):
    a_dette = fiche["reste"] > 1
    tags = []
    if fiche.get("ville"):
        tags.append(fiche["ville"])
    if fiche.get("nb_docs"):
        tags.append("%d document(s)" % fiche["nb_docs"])
    return {
        "id": fiche["id"],
        "nom": fiche.get("nom") or "",
        "nom_fr": "",
        "metier": fiche.get("metier") or "",
        "wilaya": fiche.get("wilaya"),
        "telephone": fiche.get("telephone") or "",
        "tags": tags,
        "montant": fiche["reste"] if a_dette else (fiche["chiffre"] or None),
        "montant_libelle": "DZD \u00b7 \u0627\u0644\u0628\u0627\u0642\u064a \u00b7 reste" if a_dette
        else "DZD \u00b7 \u0627\u0644\u0645\u062c\u0645\u0648\u0639 \u00b7 factur\u00e9",
        "alerte": a_dette,
        "couleur": "red" if a_dette else "blue",
        "sous_titre": tel_joli(fiche.get("telephone")) or "\u2014",
        "message": _relance(fiche) if a_dette else "",
    }


def _relance(fiche):
    return ("\u0627\u0644\u0633\u0644\u0627\u0645 \u0639\u0644\u064a\u0643\u0645 %s\u060c "
            "\u0627\u0644\u0628\u0627\u0642\u064a %s \u062f\u062c \u2014 \u0645\u0627 \u0639\u0644\u064a\u0647\u0627\u0634 \u0645\u0646 \u0648\u0642\u062a \u064a\u0646\u0627\u0633\u0628\u0643. "
            "\u0634\u0643\u0631\u0627 \u0644\u0643." % (fiche.get("nom") or "", nombre(fiche["reste"])))


# ------------------------------------------------------------------ dialogues
@c.dialogue("\u0632\u0628\u0648\u0646 \u062c\u062f\u064a\u062f \u00b7 Nouveau client", "small")
def _dialog_client():
    if k.formulaire_client_rapide("cli"):
        st.rerun()


@c.dialogue("\u0645\u0644\u0641 \u0627\u0644\u0632\u0628\u0648\u0646 \u00b7 Fiche client", "small")
def _dialog_fiche(client_id):
    client = db.one("SELECT * FROM clients WHERE id=?", (client_id,))
    if not client:
        etat.fermer(ESPACE)
        st.info("Fiche introuvable.")
        return

    docs = [d for d in documents() if d.get("client_id") == client_id]
    reste = sum(max(0.0, float(d.get("total") or 0) - total_paye(d["id"]))
                for d in docs if d.get("statut") not in ("Brouillon", "Annule"))
    fiche = dict(client)
    fiche.update({"reste": reste,
                  "chiffre": sum(float(d.get("total") or 0) for d in docs
                                 if d.get("type_doc") in ("Facture", "Recu")),
                  "nb_docs": len(docs)})
    st.markdown('<div class="karts">%s</div>'
                % cartes.carte(_en_carte(fiche),
                               db.get_param("entreprise_nom") or "",
                               db.get_param("entreprise_rip") or ""),
                unsafe_allow_html=True)

    champs.bloc_titre("\u0645\u0639\u0644\u0648\u0645\u0627\u062a \u0627\u0644\u0632\u0628\u0648\u0646", "Coordonn\u00e9es", "\u270f\ufe0f")
    suffixe = str(client_id)
    nom = champs.texte("\u0627\u0644\u0627\u0633\u0645", "Nom", requis=True, icone="\U0001f464",
                       value=client["nom"], key="fc_nom_" + suffixe)
    col1, col2 = st.columns(2)
    with col1:
        tel = champs.texte("\u0627\u0644\u0647\u0627\u062a\u0641", "T\u00e9l\u00e9phone", icone="\U0001f4f1",
                           value=client.get("telephone") or "", key="fc_tel_" + suffixe)
    with col2:
        ville = champs.texte("\u0627\u0644\u0628\u0644\u062f\u064a\u0629", "Commune / Ville",
                             value=client.get("ville") or "", key="fc_ville_" + suffixe)
    codes = wilayas.options(True)
    actuel = client.get("wilaya")
    code = champs.wilaya(index=codes.index(actuel) if actuel in codes else 0,
                         key="fc_wil_" + suffixe)
    adresse = champs.texte("\u0627\u0644\u0639\u0646\u0648\u0627\u0646", "Adresse", icone="\U0001f5fa\ufe0f",
                           value=client.get("adresse") or "", key="fc_adr_" + suffixe)
    note = champs.zone("\u0645\u0644\u0627\u062d\u0638\u0629", "Note (code portail, pr\u00e9f\u00e9rences\u2026)",
                       height=68, value=client.get("note") or "", key="fc_note_" + suffixe)

    if docs:
        champs.bloc_titre("\u0627\u0644\u0633\u062c\u0644", "Historique", "\U0001f4dc")
        for d in docs[:6]:
            st.markdown('<div style="display:flex;justify-content:space-between;padding:4px 0">'
                        '<span class="sm">%s \u00b7 %s</span><span class="money sm">%s</span></div>'
                        % (c.e(d["numero"]), c.e(d["type_doc"]), nombre(d["total"])),
                        unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    if b1.button("\U0001f4be \u062d\u0641\u0638 \u00b7 Enregistrer", type="primary",
                 use_container_width=True, key="fc_save_" + suffixe):
        db.run("UPDATE clients SET nom=?, telephone=?, ville=?, wilaya=?, adresse=?, note=? "
               "WHERE id=?", (nom, tel, ville, code, adresse, note, client_id))
        etat.fermer(ESPACE)
        c.toast("Fiche enregistr\u00e9e")
        st.rerun()
    if b2.button("\u0625\u063a\u0644\u0627\u0642 \u00b7 Fermer", use_container_width=True,
                 key="fc_close_" + suffixe):
        etat.fermer(ESPACE)
        st.rerun()
