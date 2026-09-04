# -*- coding: utf-8 -*-
"""Annuaire des artisans : recherche, cartes responsives, profil en dialogue.

Toute la liste est dessinee en un seul rendu HTML (voir ui/cartes.py) et les
filtres sont memorises dans st.session_state (voir ui/etat.py), donc revenir
sur cet ecran retrouve exactement la meme recherche.
"""
import streamlit as st

from core import artisans, db, wilayas
from core.fmt import nombre
from .. import cartes, champs, etat
from .. import components as c

ESPACE = "annuaire"
TOUS = "\u0627\u0644\u0643\u0644 - Tous les m\u00e9tiers"

TRIS = [
    ("nom", "\u0623\u0628\u062c\u062f\u064a - A\u2192Z"),
    ("note", "\u0627\u0644\u0623\u0641\u0636\u0644 - Mieux not\u00e9s"),
    ("tarif", "\u0627\u0644\u0623\u0631\u062e\u0635 - Tarif croissant"),
    ("recent", "\u0627\u0644\u0623\u062d\u062f\u062b - R\u00e9cents"),
]
LIB_TRI = [libelle for _cle, libelle in TRIS]
CLE_TRI = {libelle: cle for cle, libelle in TRIS}

DEFAUTS = {"q": "", "metier": TOUS, "wilaya": None, "dispo": False, "tri": TRIS[0][1]}


# ----------------------------------------------------------------------- ecran
def afficher():
    identifiant = etat.depuis_url(ESPACE)          # ?fiche=12 depuis une carte
    stats = artisans.statistiques()

    c.entete("\u0627\u0644\u062d\u0631\u0641\u064a\u0648\u0646 \u00b7 Annuaire des artisans",
             "\u0627\u0644\u0641\u0631\u064a\u0642 \u0648\u0627\u0644\u0645\u0642\u0627\u0648\u0644\u0648\u0646 \u00b7 votre \u00e9quipe et vos sous-traitants",
             c.pilule("%d" % stats["total"], "blue") if stats["total"] else None)

    if stats["total"]:
        c.bande_kpi([
            {"icone": "\U0001f477", "label": "\u0627\u0644\u062d\u0631\u0641\u064a\u0648\u0646 / Artisans",
             "valeur": nombre(stats["total"])},
            {"icone": "\u2705", "label": "\u0645\u062a\u0627\u062d / Disponibles",
             "valeur": nombre(stats["disponibles"])},
            {"icone": "\U0001f4b0", "label": "\u0645\u062a\u0648\u0633\u0637 \u0627\u0644\u064a\u0648\u0645\u064a\u0629 / Tarif moyen",
             "valeur": nombre(stats["tarif_moyen"]), "unite": "DZD"},
        ])

    gauche, droite = st.columns(2)
    if gauche.button("\u2795 \u062d\u0631\u0641\u064a \u062c\u062f\u064a\u062f  \u00b7  Nouvel artisan", type="primary",
                     use_container_width=True, key="an_add"):
        _dialog_artisan()
    actifs = etat.nb_actifs(ESPACE, DEFAUTS)
    if droite.button("\u267b\ufe0f \u0645\u0633\u062d \u0627\u0644\u0645\u0631\u0634\u062d\u0627\u062a  \u00b7  Effacer les filtres (%d)" % actifs,
                     use_container_width=True, key="an_reset", disabled=not actifs):
        etat.reinitialiser(ESPACE, DEFAUTS)
        st.rerun()

    _filtres()

    metier = etat.filtre(ESPACE, "metier", TOUS)
    fiches = artisans.lister(
        recherche=etat.filtre(ESPACE, "q", "") or "",
        metier=None if metier in (None, TOUS) else metier,
        wilaya=etat.filtre(ESPACE, "wilaya"),
        dispo_seulement=bool(etat.filtre(ESPACE, "dispo", False)),
        tri=CLE_TRI.get(etat.filtre(ESPACE, "tri", TRIS[0][1]), "nom"))

    if not fiches:
        if stats["total"]:
            c.vide("\U0001f50d", "\u0644\u0627 \u0646\u062a\u064a\u062c\u0629 \u00b7 Aucun r\u00e9sultat",
                   "Changez de m\u00e9tier ou de wilaya, ou effacez les filtres.")
        else:
            c.vide("\U0001f477", "\u0627\u0644\u062f\u0641\u062a\u0631 \u0641\u0627\u0631\u063a \u00b7 Annuaire vide",
                   "Ajoutez les artisans avec qui vous travaillez : nom, m\u00e9tier, "
                   "wilaya et num\u00e9ro. Vous les appellerez ensuite en un tap.")
        return

    cartes.bandeau_resultats(len(fiches), "\u062d\u0631\u0641\u064a", "artisan(s)", actifs)
    cartes.grille([_en_carte(f) for f in fiches],
                  entreprise=db.get_param("entreprise_nom") or "",
                  rip=db.get_param("entreprise_rip") or "")

    if identifiant:
        _dialog_profil(identifiant)


def _filtres():
    """Recherche en ligne + tiroir de filtres : aucune colonne laterale."""
    actifs = etat.nb_actifs(ESPACE, DEFAUTS)
    champs.texte("\u0628\u062d\u062b", "Rechercher un nom, une sp\u00e9cialit\u00e9, un num\u00e9ro",
                 icone="\U0001f50d", placeholder="Ammi Salah, tableau, 0661\u2026",
                 **etat.lie(ESPACE, "q", ""))
    with st.expander("\u2699\ufe0f  \u0645\u0631\u0634\u062d\u0627\u062a \u00b7 Filtres" +
                     (("  (%d)" % actifs) if actifs else ""),
                     expanded=bool(actifs)):
        col1, col2 = st.columns(2)
        with col1:
            champs.choix("\u0627\u0644\u0645\u0647\u0646\u0629", "M\u00e9tier",
                         [TOUS] + list(artisans.METIERS), icone="\U0001f6e0\ufe0f",
                         **etat.lie(ESPACE, "metier", TOUS))
        with col2:
            champs.wilaya(**etat.lie(ESPACE, "wilaya", None))
        col3, col4 = st.columns(2)
        with col3:
            champs.choix("\u0627\u0644\u062a\u0631\u062a\u064a\u0628", "Trier par", LIB_TRI,
                         icone="\u2195\ufe0f", **etat.lie(ESPACE, "tri", TRIS[0][1]))
        with col4:
            champs.bascule("\u0627\u0644\u0645\u062a\u0627\u062d\u064a\u0646 \u0641\u0642\u0637",
                           "Disponibles seulement",
                           **etat.lie(ESPACE, "dispo", False))
    cartes.puces_filtres(_puces())


def _puces():
    """Resume des filtres actifs, affiche sous la recherche."""
    puces = []
    metier = etat.filtre(ESPACE, "metier", TOUS)
    if metier and metier != TOUS:
        puces.append(("\U0001f6e0\ufe0f " + str(metier), True))
    code = etat.filtre(ESPACE, "wilaya")
    if code:
        puces.append(("\U0001f4cd " + wilayas.libelle(code, ""), True))
    if etat.filtre(ESPACE, "dispo", False):
        puces.append(("\u2705 \u0645\u062a\u0627\u062d \u00b7 dispo", True))
    tri = etat.filtre(ESPACE, "tri", TRIS[0][1])
    if tri and tri != TRIS[0][1]:
        puces.append(("\u2195\ufe0f " + str(tri), False))
    return puces


def _en_carte(fiche):
    dispo = int(fiche.get("disponible") or 0) == 1
    tags = []
    if fiche.get("commune"):
        tags.append(fiche["commune"])
    if fiche.get("specialites"):
        tags += [t.strip() for t in str(fiche["specialites"]).split(",") if t.strip()][:2]
    return {
        "id": fiche["id"],
        "nom": fiche.get("nom") or "",
        "nom_fr": fiche.get("nom_fr") or "",
        "metier": fiche.get("metier") or "",
        "wilaya": fiche.get("wilaya"),
        "telephone": fiche.get("telephone") or "",
        "note": fiche.get("note"),
        "tags": tags,
        "montant": fiche.get("tarif_jour") or None,
        "montant_libelle": "DZD \u00b7 \u0627\u0644\u064a\u0648\u0645\u064a\u0629 \u00b7 par jour",
        "couleur": "green" if dispo else "grey",
        "disponible": dispo,
        "badge": "\u0645\u062a\u0627\u062d \u00b7 dispo" if dispo else "\u0645\u0634\u063a\u0648\u0644 \u00b7 occup\u00e9",
        "message": "\u0627\u0644\u0633\u0644\u0627\u0645 \u0639\u0644\u064a\u0643\u0645\u060c \u0639\u0646\u062f\u064a \u062e\u062f\u0645\u0629 \u2014 "
                   "\u0648\u0627\u0634 \u0631\u0627\u0643 \u0645\u062a\u0627\u062d\u061f",
    }


# ------------------------------------------------------------------- dialogues
@c.dialogue("\u0645\u0644\u0641 \u0627\u0644\u062d\u0631\u0641\u064a \u00b7 Profil artisan", "small")
def _dialog_profil(identifiant):
    fiche = artisans.charger(identifiant)
    if not fiche:
        etat.fermer(ESPACE)
        st.info("Fiche introuvable.")
        return

    st.markdown('<div class="karts">%s</div>'
                % cartes.carte(_en_carte(fiche),
                               db.get_param("entreprise_nom") or "",
                               db.get_param("entreprise_rip") or ""),
                unsafe_allow_html=True)
    if fiche.get("remarque"):
        st.caption(fiche["remarque"])

    haut1, haut2 = st.columns(2)
    if haut1.button("\U0001f501 \u062a\u0628\u062f\u064a\u0644 \u0627\u0644\u062a\u0648\u0627\u0641\u0631 \u00b7 Disponibilit\u00e9",
                    use_container_width=True, key="an_dispo_%s" % identifiant):
        artisans.basculer_dispo(identifiant)
        st.rerun()
    if haut2.button("\U0001f5d1\ufe0f \u062d\u0630\u0641 \u00b7 Supprimer", use_container_width=True,
                    key="an_del_%s" % identifiant):
        artisans.supprimer(identifiant)
        etat.fermer(ESPACE)
        c.toast("Fiche supprim\u00e9e", "\U0001f5d1\ufe0f")
        st.rerun()

    champs.bloc_titre("\u062a\u0639\u062f\u064a\u0644", "Modifier la fiche", "\u270f\ufe0f")
    _formulaire(fiche, identifiant)


@c.dialogue("\u062d\u0631\u0641\u064a \u062c\u062f\u064a\u062f \u00b7 Nouvel artisan", "small")
def _dialog_artisan():
    _formulaire({}, None)


def _formulaire(fiche, artisan_id=None):
    suffixe = str(artisan_id or "new")
    nom = champs.texte("\u0627\u0644\u0627\u0633\u0645", "Nom (arabe ou latin)", requis=True,
                       icone="\U0001f464", value=fiche.get("nom") or "",
                       key="an_nom_" + suffixe, placeholder="\u0639\u0645\u064a \u0635\u0627\u0644\u062d")
    col1, col2 = st.columns(2)
    with col1:
        nom_fr = champs.texte("\u0627\u0644\u0627\u0633\u0645 \u0628\u0627\u0644\u0644\u0627\u062a\u064a\u0646\u064a\u0629", "Nom en fran\u00e7ais",
                              value=fiche.get("nom_fr") or "", key="an_nomfr_" + suffixe,
                              placeholder="Ammi Salah")
    with col2:
        telephone = champs.texte("\u0627\u0644\u0647\u0627\u062a\u0641", "T\u00e9l\u00e9phone", requis=True,
                                 icone="\U0001f4f1", value=fiche.get("telephone") or "",
                                 key="an_tel_" + suffixe, placeholder="0661 22 33 44")
    liste_metiers = list(artisans.METIERS)
    actuel = fiche.get("metier")
    metier = champs.choix("\u0627\u0644\u0645\u0647\u0646\u0629", "M\u00e9tier", liste_metiers,
                          icone="\U0001f6e0\ufe0f",
                          index=liste_metiers.index(actuel) if actuel in liste_metiers else 0,
                          key="an_met_" + suffixe)

    from core import wilayas
    codes = wilayas.options(True)
    code_actuel = fiche.get("wilaya")
    try:
        code_actuel = int(code_actuel) if code_actuel else None
    except (TypeError, ValueError):
        code_actuel = None
    wilaya = champs.wilaya(index=codes.index(code_actuel) if code_actuel in codes else 0,
                           key="an_wil_" + suffixe)
    commune = champs.texte("\u0627\u0644\u0628\u0644\u062f\u064a\u0629", "Commune",
                           value=fiche.get("commune") or "", key="an_com_" + suffixe,
                           placeholder="Bab Ezzouar")

    col3, col4 = st.columns(2)
    with col3:
        tarif = champs.montant("\u0627\u0644\u064a\u0648\u0645\u064a\u0629", "Tarif par jour (DZD)",
                               value=float(fiche.get("tarif_jour") or 0),
                               key="an_tar_" + suffixe)
    with col4:
        note = champs.nombre("\u0627\u0644\u062a\u0642\u064a\u064a\u0645", "Note sur 5", icone="\u2b50",
                             min_value=0.0, max_value=5.0, step=0.5,
                             value=float(fiche.get("note") or 0), key="an_note_" + suffixe)
    dispo = champs.bascule("\u0645\u062a\u0627\u062d \u062d\u0627\u0644\u064a\u0627", "Disponible en ce moment",
                           value=int(fiche.get("disponible") or 0) == 1 if fiche else True,
                           key="an_dispo_c_" + suffixe)
    specialites = champs.texte("\u0627\u0644\u062a\u062e\u0635\u0635\u0627\u062a", "Sp\u00e9cialit\u00e9s (s\u00e9par\u00e9es par des virgules)",
                               value=fiche.get("specialites") or "", key="an_spe_" + suffixe,
                               placeholder="tableau, mise \u00e0 la terre, VMC")
    rip = champs.texte("RIP / CCP", "Compte BaridiMob (optionnel)", icone="\U0001f3e6",
                       value=fiche.get("rip") or "", key="an_rip_" + suffixe)
    remarque = champs.zone("\u0645\u0644\u0627\u062d\u0637\u0629", "Remarque", height=68,
                           value=fiche.get("remarque") or "", key="an_rem_" + suffixe)

    if st.button("\U0001f4be \u062d\u0641\u0637 \u00b7 Enregistrer", type="primary",
                 use_container_width=True, key="an_save_" + suffixe,
                 disabled=not (nom or "").strip()):
        artisans.enregistrer({
            "nom": nom, "nom_fr": nom_fr, "metier": metier, "wilaya": wilaya,
            "commune": commune, "telephone": telephone, "tarif_jour": tarif,
            "note": note, "specialites": specialites,
            "disponible": 1 if dispo else 0, "rip": rip, "remarque": remarque,
        }, artisan_id)
        etat.fermer(ESPACE)
        c.toast("Fiche enregistr\u00e9e")
        st.rerun()
