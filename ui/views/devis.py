# -*- coding: utf-8 -*-
"""\u00c9cran Devis & Factures : liste filtrable + \u00e9diteur de postes avec marge en direct."""
import json
import os
import uuid
from datetime import date

import pandas as pd
import streamlit as st

from core import catalog, db, docs, parsing, pdf
from core.fmt import (arrondi_commercial, dz, lien_viber, lien_whatsapp, mois_cle,
                         mois_libelle, nombre)
from core.metier import (COULEUR_STATUT, ETAPES_LIB, MODES_PAIEMENT, UNITES,
                            cout_lignes, marge_ligne, message_devis, sante_marge,
                            total_lignes, total_paye)
from .. import components as c
from ..theme import JETONS
from . import _communs as k


def _vider(cle):
    """Vide un widget au run suivant via le marqueur pre_clear_<cle>."""
    if st.session_state.pop("pre_clear_" + cle, False):
        st.session_state.pop(cle, None)


def _sel_diff(cle):
    """Selection differee, avec repli si le module commun est ancien."""
    fonction = getattr(k, "selection_differee", None)
    if fonction:
        return fonction(cle)
    valeur = st.session_state.pop("pre_" + cle, None)
    if valeur is not None:
        st.session_state.pop(cle, None)
    return valeur

FILTRES = ["Tous", "Brouillons", "Envoy\u00e9s", "Accept\u00e9s", "Factures", "Impay\u00e9s"]


def afficher():
    if st.session_state.get("doc_ouvert"):
        _editeur(st.session_state["doc_ouvert"])
    else:
        _liste()


# ==========================================================================
#  LISTE
# ==========================================================================
def _liste():
    tous = docs.documents()
    total_general = sum(float(d.get("total") or 0) for d in tous)
    c.entete(c.bi("\u0639\u0631\u0648\u0636 \u0627\u0644\u0623\u0633\u0639\u0627\u0631", "Devis & Factures"),
             "%d document(s) \u00b7 %s" % (len(tous), dz(total_general)))

    col1, col2 = st.columns([1, 1])
    if col1.button(c.bi("\uff0b  \u0639\u0631\u0636 \u0633\u0639\u0631 \u062c\u062f\u064a\u062f", "Nouveau devis"),
                   type="primary", use_container_width=True):
        st.session_state["ouvrir_dialog_devis"] = True
    if col2.button("\u26a1  Devis \u00c9clair", use_container_width=True):
        st.session_state["ouvrir_dialog_devis"] = True
        st.session_state["focus_eclair"] = True

    if st.session_state.pop("ouvrir_dialog_devis", False):
        st.session_state["dialog_devis_actif"] = True
    if st.session_state.get("dialog_devis_actif"):
        _dialog_nouveau_devis()

    recherche = st.text_input("Rechercher", key="rech_doc", label_visibility="collapsed",
                              placeholder="\U0001f50e  Rechercher un num\u00e9ro, un client, un chantier\u2026")
    filtre = c.pilules_filtre("Filtre", FILTRES, "filtre_doc", "Tous")

    liste = docs.documents(recherche=recherche)
    liste = _appliquer_filtre(liste, filtre)

    if not liste:
        c.vide("\U0001f4c4", "Aucun document ici",
               "Changez de filtre, ou cr\u00e9ez un devis en partant d'un mod\u00e8le m\u00e9tier.")
        return

    # regroupement par mois avec total de groupe : on voit tout de suite le rythme
    groupes = {}
    for doc in liste:
        groupes.setdefault(mois_cle(doc.get("date_doc")), []).append(doc)

    for cle in sorted(groupes, reverse=True):
        lot = groupes[cle]
        somme = sum(float(d.get("total") or 0) for d in lot)
        st.markdown('<div style="display:flex;justify-content:space-between;align-items:baseline;'
                    'margin:18px 0 6px"><b>%s</b><span class="sm muted money">%s</span></div>'
                    % (c.e(mois_libelle(lot[0].get("date_doc"))), dz(somme)),
                    unsafe_allow_html=True)
        for doc in lot:
            reste = float(doc.get("total") or 0) - total_paye(doc["id"])
            with st.container(border=True):
                c.carte_document(doc, reste if doc.get("statut") not in ("Brouillon", "Annule") else None)
                b1, b2 = st.columns([1, 1])
                if b1.button("Ouvrir", key="op_%d" % doc["id"], use_container_width=True):
                    k.ouvrir_document(doc["id"])
                if b2.button("Dupliquer", key="du_%d" % doc["id"], use_container_width=True):
                    nouveau = docs.dupliquer(doc["id"])
                    c.toast("Copie cr\u00e9\u00e9e")
                    k.ouvrir_document(nouveau)


def _appliquer_filtre(liste, filtre):
    if filtre == "Brouillons":
        return [d for d in liste if d["statut"] == "Brouillon"]
    if filtre == "Envoy\u00e9s":
        return [d for d in liste if d["statut"] == "Envoye"]
    if filtre == "Accept\u00e9s":
        return [d for d in liste if d["statut"] in ("Accepte", "Facture")]
    if filtre == "Factures":
        return [d for d in liste if d["type_doc"] in ("Facture", "Recu")]
    if filtre == "Impay\u00e9s":
        return [d for d in liste
                if d["statut"] not in ("Brouillon", "Annule")
                and float(d.get("total") or 0) - total_paye(d["id"]) > 1]
    return liste


# ==========================================================================
#  DIALOGUE : NOUVEAU DEVIS (mod\u00e8les m\u00e9tier / \u00c9clair / vierge)
# ==========================================================================
@c.dialogue(c.bi("\u0639\u0631\u0636 \u0633\u0639\u0631 \u062c\u062f\u064a\u062f", "Nouveau devis"))
def _dialog_nouveau_devis():
    st.session_state.setdefault("tpl_choisis", [])

    client_id = k.selecteur_client("Client *", "nd_client",
                                   valeur=_sel_diff("nd_client"))
    with st.expander("\uff0b  Cr\u00e9er un client en 5 secondes"):
        nouveau = k.formulaire_client_rapide("nd")
        if nouveau:
            st.session_state["pre_nd_client"] = nouveau
            st.rerun()

    chantier_id = k.selecteur_chantier("Chantier (optionnel)", "nd_chantier", client_id=client_id,
                                       valeur=_sel_diff("nd_chantier"))
    with st.expander("\uff0b  Nouveau chantier"):
        nouveau_ch = k.formulaire_chantier_rapide(client_id, "nd_ch")
        if nouveau_ch:
            st.session_state["pre_nd_chantier"] = nouveau_ch
            st.rerun()

    choisis = st.session_state["tpl_choisis"]
    principaux, autres = catalog.templates_ordonnes()

    def _grille_modeles(noms, prefixe):
        colonnes = st.columns(2)
        for i, nom in enumerate(noms):
            modele = catalog.TEMPLATES[nom]
            actif = nom in choisis
            libelle = "%s  %s\n\n%d postes%s" % (modele["icone"], nom, len(modele["postes"]),
                                                 "  \u2713" if actif else "")
            if colonnes[i % 2].button(libelle, key="%s_%d" % (prefixe, i), use_container_width=True,
                                      type="primary" if actif else "secondary"):
                if actif:
                    choisis.remove(nom)
                else:
                    choisis.append(nom)
                st.rerun()

    if autres:
        st.markdown('<div class="sec">%s</div>'
                    % c.bi("\u0646\u0645\u0627\u0630\u062c \u0645\u0647\u0646\u062a\u0643 \u2014 \u0642\u0627\u0628\u0644\u0629 \u0644\u0644\u062c\u0645\u0639",
                           "Mod\u00e8les de votre m\u00e9tier \u2014 cumulables"), unsafe_allow_html=True)
        st.caption(c.bi("\u0645\u062d\u0636\u0651\u0631\u0629 \u062d\u0633\u0628 \u0645\u0647\u0646\u062a\u0643 \u0648\u0623\u0633\u0639\u0627\u0631\u0643 \u0627\u0644\u0645\u0639\u062a\u0627\u062f\u0629",
                        "Pr\u00e9-remplis selon votre m\u00e9tier et vos prix habituels."))
        _grille_modeles(principaux, "tplm")
        with st.expander(c.bi("\u0645\u064a\u0627\u062f\u064a\u0646 \u0623\u062e\u0631\u0649", "Autres m\u00e9tiers")):
            _grille_modeles(autres, "tplo")
    else:
        st.markdown('<div class="sec">Mod\u00e8les m\u00e9tier \u2014 cumulables</div>', unsafe_allow_html=True)
        st.caption("S\u00e9lectionnez un ou plusieurs corps de m\u00e9tier : les postes et les prix "
                   "habituels sont pr\u00e9-remplis, vous ajustez ensuite.")
        _grille_modeles(principaux, "tplm")

    if choisis:
        apercu = []
        for nom in choisis:
            apercu += catalog.postes_template(nom)
        st.markdown('<div class="msg">%d postes pr\u00e9-remplis \u00b7 base de %s</div>'
                    % (len(apercu), dz(total_lignes(apercu))), unsafe_allow_html=True)
        if st.button("Cr\u00e9er le devis avec ces mod\u00e8les", type="primary", use_container_width=True):
            _creer_et_ouvrir(client_id, chantier_id, apercu)

    st.markdown('<div class="sec">ou dictez votre devis</div>', unsafe_allow_html=True)
    phrase = st.text_input("Devis \u00c9clair", key="nd_eclair", label_visibility="collapsed",
                           placeholder="\u26a1  45 m2 peinture 550 + 12 prises 2800 + nettoyage 5000")
    if phrase:
        lignes = parsing.analyser(phrase)
        if lignes:
            st.markdown('<div class="msg">%s</div>' % "<br>".join(
                "\u2022 %s \u2014 %s %s \u00d7 %s" % (c.e(l["description"]), nombre(l["quantite"]),
                                                      c.e(l["unite"]), nombre(l["prix_unitaire"]))
                for l in lignes), unsafe_allow_html=True)
            if st.button("Cr\u00e9er le devis \u00c9clair (%s)" % dz(total_lignes(lignes)),
                         type="primary", use_container_width=True):
                _creer_et_ouvrir(client_id, chantier_id, lignes)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    if col1.button("\uff0b  Devis vierge", use_container_width=True):
        _creer_et_ouvrir(client_id, chantier_id, [catalog.ligne_vide()])
    if col2.button("Annuler", use_container_width=True):
        st.session_state["dialog_devis_actif"] = False
        st.rerun()


def _creer_et_ouvrir(client_id, chantier_id, lignes):
    doc_id = docs.creer_document(client_id, chantier_id, "Devis", lignes)
    st.session_state["dialog_devis_actif"] = False
    st.session_state["tpl_choisis"] = []
    k.ouvrir_document(doc_id)


# ==========================================================================
#  \u00c9DITEUR
# ==========================================================================
def _charger_buffer(doc_id):
    if st.session_state.get("doc_lignes_id") != doc_id:
        lignes = []
        for l in docs.charger_lignes(doc_id):
            ligne = catalog.ligne_vide(l["description"], l["unite"], l["quantite"],
                                       l["prix_unitaire"], l["cout_materiaux"], l["cout_pose"])
            ligne["uid"] = uuid.uuid4().hex[:8]
            lignes.append(ligne)
        if not lignes:
            vide = catalog.ligne_vide()
            vide["uid"] = uuid.uuid4().hex[:8]
            lignes = [vide]
        st.session_state["lignes_edition"] = lignes
        st.session_state["doc_lignes_id"] = doc_id
        st.session_state["etape_devis"] = 1
    return st.session_state["lignes_edition"]


def _sauver(doc_id, lignes, remise):
    db.run("UPDATE devis_factures SET remise=? WHERE id=?", (float(remise or 0), doc_id))
    return docs.remplacer_lignes(doc_id, lignes)



def _stepper(etape):
    """Fil d'Ariane : etape 1 = infos client/chantier, etape 2 = tableau des postes."""

    def chip(numero, ar, fr, active):
        fond = "var(--bleu-d)" if active else "var(--surf2)"
        coul = "#1A5FA5" if active else "var(--gris)"
        return ('<span style="background:%s;color:%s;border-radius:999px;padding:6px 14px;'
                'font-size:13px;font-weight:700;white-space:nowrap">%s&nbsp;%s (%s)</span>'
                % (fond, coul, numero, ar, fr))

    st.markdown('<div style="display:flex;align-items:center;gap:8px;margin:2px 0 14px;'
                'direction:rtl">'
                + chip("①", "معلومات الزبون والورشة", "Infos", etape == 1)
                + '<span style="color:var(--gris)">←</span>'
                + chip("②", "جدول البنود", "Tableau", etape == 2)
                + "</div>", unsafe_allow_html=True)


def _etape_infos(doc, lignes):
    """Étape 1 : client + chantier + note, puis le récapitulatif du tableau rempli."""
    doc_id = doc["id"]
    remise = float(doc.get("remise") or 0)
    total = max(0.0, total_lignes(lignes) - remise)
    statut = doc.get("statut") or "Brouillon"

    # ------------------------------------------------------ client & chantier
    with st.container(border=True):
        st.markdown('<div class="sec" style="margin-top:0">%s</div>'
                    % c.bi("الزبون والورشة", "Client & chantier"),
                    unsafe_allow_html=True)
        cle_cli = "einfo_client_%d" % doc_id
        client_id = k.selecteur_client(c.bi("الزبون", "Client") + " *", cle_cli,
                                       valeur=_sel_diff(cle_cli) or doc.get("client_id"))
        with st.expander(c.bi("＋ زبون جديد في 5 ثوان",
                              "Créer un client en 5 secondes")):
            nouveau = k.formulaire_client_rapide("einfo_%d" % doc_id)
            if nouveau:
                st.session_state["pre_" + cle_cli] = nouveau
                st.rerun()
        cle_ch = "einfo_chantier_%d" % doc_id
        chantier_id = k.selecteur_chantier(c.bi("الورشة", "Chantier"), cle_ch,
                                           client_id=client_id,
                                           valeur=_sel_diff(cle_ch) or doc.get("chantier_id"))
        with st.expander(c.bi("＋ ورشة جديدة", "Nouveau chantier")):
            nouveau_ch = k.formulaire_chantier_rapide(client_id, "einfo_ch_%d" % doc_id)
            if nouveau_ch:
                st.session_state["pre_" + cle_ch] = nouveau_ch
                st.rerun()
        note = st.text_area(c.bi("ملاحظة على الوثيقة", "Note sur le document"),
                            value=doc.get("note") or "", key="einfo_note_%d" % doc_id)
        if st.button(c.bi("💾 حفظ المعلومات", "Enregistrer les infos"),
                     type="primary", use_container_width=True):
            db.run("UPDATE devis_factures SET client_id=?, chantier_id=?, note=? WHERE id=?",
                   (client_id, chantier_id, note, doc_id))
            c.toast(c.bi("✓ تم حفظ المعلومات", "Informations enregistrées"))
            st.rerun()

    # ------------------------------------------------------ recapitulatif du tableau rempli
    remplies = [l for l in lignes if (l.get("description") or "").strip()]
    if remplies:
        with st.container(border=True):
            st.markdown('<div class="sec" style="margin-top:0">%s</div>'
                        % c.bi("✓ الجدول المعبأ", "Tableau rempli"),
                        unsafe_allow_html=True)
            resume = pd.DataFrame([{
                c.bi("التعيين", "Désignation"): l["description"],
                c.bi("الكمية", "Qté"): l.get("quantite") or 0,
                c.bi("الوحدة", "Unité"): l.get("unite") or "U",
                "P.U. DZD": l.get("prix_unitaire") or 0,
                c.bi("المجموع", "Total"): round((l.get("quantite") or 0)
                                                                             * (l.get("prix_unitaire") or 0)),
            } for l in remplies])
            st.dataframe(resume, use_container_width=True, hide_index=True)
            st.markdown('<div style="display:flex;justify-content:space-between;'
                        'align-items:baseline"><span class="sm muted">%s</span>'
                        '<span class="money" style="font-size:22px">%s</span></div>'
                        % (c.bi("المجموع · بدون TVA",
                                "Total client · sans TVA"), dz(total)),
                        unsafe_allow_html=True)
        if st.button(c.bi("✏️ عدّل الجدول", "Modifier le tableau"),
                     use_container_width=True):
            st.session_state["etape_devis"] = 2
            st.rerun()
    else:
        c.vide("🧾", c.bi("الجدول فارغ بعد", "Tableau encore vide"),
               c.bi("احفظ المعلومات ثم انتقل للخطوة ② لملء البنود",
                    "Enregistrez les infos puis passez à l'etape 2."))

    if st.button(c.bi("التالي: جدول البنود", "Suivant : le tableau") + "  ←",
                 type="primary", use_container_width=True):
        st.session_state["etape_devis"] = 2
        st.rerun()

    # ------------------------------------------------------ suite du parcours
    c.section(c.bi("\u0645\u0627 \u0628\u0639\u062f\u0647\u0627", "Suite du parcours"))
    s1, s2, s3 = st.columns(3)
    suivant = docs.statut_suivant(statut)
    if suivant and s1.button("\u2192 Marquer %s" % ETAPES_LIB[suivant], use_container_width=True):
        docs.changer_statut(doc_id, suivant)
        c.toast("Statut : %s" % ETAPES_LIB[suivant])
        st.rerun()
    if doc["type_doc"] == "Devis" and s2.button("\U0001f9fe Transformer en facture",
                                                use_container_width=True):
        _sauver(doc_id, lignes, remise)
        nouveau = docs.convertir(doc_id, "Facture")
        c.toast("Facture cr\u00e9\u00e9e")
        k.ouvrir_document(nouveau)
    if s3.button("\U0001f5d1\ufe0f Supprimer le document", use_container_width=True):
        docs.supprimer(doc_id)
        st.session_state.pop("doc_ouvert", None)
        st.session_state.pop("doc_lignes_id", None)
        c.toast("Document supprim\u00e9", "\U0001f5d1\ufe0f")
        st.rerun()

    # ------------------------------------------------------ encaissements
    paiements = db.q("SELECT * FROM paiements WHERE document_id=? ORDER BY date_paiement", (doc_id,))
    paye = sum(float(p["montant"]) for p in paiements)
    if doc["type_doc"] != "Devis" or paye:
        c.section(c.bi("\u0627\u0644\u062a\u062d\u0635\u064a\u0644\u0627\u062a", "Encaissements"))
        with st.container(border=True):
            c.ligne_stat("D\u00e9j\u00e0 vers\u00e9", dz(paye), JETONS["vert"])
            c.ligne_stat("Reste \u00e0 payer", dz(max(0.0, total - paye)),
                         JETONS["rouge"] if total - paye > 1 else JETONS["vert"])
            e1, e2 = st.columns([1.2, 1])
            montant = e1.number_input("Montant re\u00e7u", min_value=0.0, step=1000.0,
                                      value=float(max(0.0, total - paye)), key="enc_%d" % doc_id)
            mode = e2.selectbox("Mode", MODES_PAIEMENT, key="encm_%d" % doc_id)
            if st.button("Enregistrer l'encaissement", type="primary", use_container_width=True,
                         disabled=montant <= 0):
                docs.enregistrer_paiement(doc_id, montant, mode)
                c.toast("Paiement enregistr\u00e9 : %s" % dz(montant))
                st.rerun()



def _editeur(doc_id):
    doc = docs.charger_document(doc_id)
    if not doc:
        st.session_state.pop("doc_ouvert", None)
        st.rerun()

    lignes = _charger_buffer(doc_id)
    statut = doc.get("statut") or "Brouillon"

    haut1, haut2 = st.columns([3, 1])
    with haut1:
        c.entete(doc["numero"] or "Document",
                 "%s \u00b7 %s" % (doc.get("client") or "Sans client", doc.get("chantier") or "sans chantier"),
                 c.pilule(ETAPES_LIB.get(statut, statut), COULEUR_STATUT.get(statut, "grey")))
    if haut2.button("\u2715  Fermer", use_container_width=True):
        st.session_state.pop("doc_ouvert", None)
        st.session_state.pop("lignes_edition", None)
        st.session_state.pop("doc_lignes_id", None)
        st.session_state.pop("pdf_pret", None)
        st.session_state.pop("grid_v", None)
        st.session_state.pop("etape_devis", None)
        st.rerun()

    etape = st.session_state.get("etape_devis", 1)
    _stepper(etape)
    if etape == 1:
        _etape_infos(doc, lignes)
        return

    if st.button(c.bi("① رجوع: معلومات الزبون والورشة", "Retour aux infos"),
                 key="retour_infos"):
        st.session_state["etape_devis"] = 1
        st.rerun()

    remise = float(doc.get("remise") or 0)

    # ------------------------------------------------------ suggestions du metier
    suggestions = catalog.suggestions_metier()
    if suggestions:
        _vider("sugg_poste")
        options = [None] + list(range(len(suggestions)))
        choix = st.selectbox(
            c.bi("اقتراحات مهنتك", "Suggestions"),
            options, key="sugg_poste",
            format_func=lambda i: ("%s · %s DZD/%s" % (suggestions[i]["libelle"],
                                                          nombre(suggestions[i]["prix_unitaire"]),
                                                          suggestions[i]["unite"]))
            if isinstance(i, int)
            else c.bi("— اختر بندًا جاهزًا يُدرج في الجدول —",
                      "Choisir une prestation"))
        if isinstance(choix, int):
            s = suggestions[choix]
            lignes.append(catalog.ligne_vide(s["libelle"], s["unite"], 1, s["prix_unitaire"],
                                             s["cout_materiaux"], s["cout_pose"]))
            st.session_state["pre_clear_sugg_poste"] = True
            st.session_state["grid_v"] = st.session_state.get("grid_v", 0) + 1
            st.rerun()

    # ------------------------------------------------------ postes : tableau editable
    c.section(c.bi("بنود العرض", "Postes du devis") + " · %d" % len(lignes))
    st.caption(c.bi("🔒 عمودا المواد/العمل خاصان بك ولا يظهران في الـ PDF",
                    "Coûts mat./pose : privés, jamais sur le PDF client."))
    colonnes_df = ["description", "quantite", "unite", "prix_unitaire",
                   "cout_materiaux", "cout_pose"]
    donnees = pd.DataFrame([{cle: l.get(cle) for cle in colonnes_df} for l in lignes],
                           columns=colonnes_df)
    edite = st.data_editor(
        donnees, key="grid_%d_v%d" % (doc_id, st.session_state.get("grid_v", 0)),
        num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={
            "description": st.column_config.TextColumn(c.bi("التعيين", "Désignation"),
                                                       width="large"),
            "quantite": st.column_config.NumberColumn(c.bi("الكمية", "Qté"),
                                                      min_value=0.0, step=1.0),
            "unite": st.column_config.SelectboxColumn(c.bi("الوحدة", "Unité"),
                                                      options=UNITES),
            "prix_unitaire": st.column_config.NumberColumn(c.bi("سعر الوحدة", "P.U. DZD"),
                                                           min_value=0.0, step=100.0),
            "cout_materiaux": st.column_config.NumberColumn(c.bi("المواد", "Coût mat."),
                                                            min_value=0.0, step=50.0),
            "cout_pose": st.column_config.NumberColumn(c.bi("العمل", "Coût pose"),
                                                       min_value=0.0, step=50.0),
        })

    def _nombre(valeur):
        try:
            if valeur is None or pd.isna(valeur):
                return 0.0
            return float(valeur)
        except (TypeError, ValueError):
            return 0.0

    lignes[:] = [catalog.ligne_vide(str(r.get("description") or "").strip(),
                                    str(r.get("unite") or "U"),
                                    _nombre(r.get("quantite")), _nombre(r.get("prix_unitaire")),
                                    _nombre(r.get("cout_materiaux")), _nombre(r.get("cout_pose")))
                 for r in edite.to_dict("records")
                 if str(r.get("description") or "").strip() or _nombre(r.get("prix_unitaire")) > 0]

    # ------------------------------------------------------ marge en direct
    brut = total_lignes(lignes)
    cout = cout_lignes(lignes)
    total = max(0.0, brut - remise)
    marge = total - cout
    marge_pct = (marge / total * 100) if total else 0.0
    couleur, libelle_sante = sante_marge(marge_pct if cout > 0 else None)
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        col1.markdown(
            '<div class="xs muted" style="font-weight:650">%s</div>'
            '<div style="font-size:20px;font-weight:780">%s <span class="sm muted">DZD · %s %%</span></div>'
            % (c.bi("الهامش المتوقع (خاص بك)",
                    "MARGE PRÉVISIONNELLE (privée)"),
               nombre(marge), nombre(marge_pct)), unsafe_allow_html=True)
        col2.markdown('<div style="text-align:right">%s</div>' % c.pilule(libelle_sante, couleur),
                      unsafe_allow_html=True)
        c.barre_repartition([("Coût interne", cout, JETONS["ambre"]),
                             ("Marge", max(0.0, marge), JETONS["vert"])])

    # ------------------------------------------------------ ajout de postes
    add1, add2 = st.columns(2)
    if add1.button(c.bi("＋  بند فارغ", "Poste vide"), use_container_width=True):
        lignes.append(catalog.ligne_vide())
        st.session_state["grid_v"] = st.session_state.get("grid_v", 0) + 1
        st.rerun()
    if add2.button(c.bi("📚  مكتبة الأسعار", "Bibliothèque"),
                   use_container_width=True):
        st.session_state["dialog_biblio"] = True
    if st.session_state.get("dialog_biblio"):
        _dialog_bibliotheque(lignes)

    _vider("edit_eclair")
    phrase = st.text_input("Ajout Éclair", key="edit_eclair", label_visibility="collapsed",
                           placeholder="⚡  Ajouter en dictant : 20 m2 faïence 1400")
    if phrase:
        if st.button(c.bi("أضف هذه البنود", "Ajouter ces postes"),
                     use_container_width=True):
            for ligne in parsing.analyser(phrase):
                lignes.append(ligne)
            st.session_state["pre_clear_edit_eclair"] = True
            st.session_state["grid_v"] = st.session_state.get("grid_v", 0) + 1
            st.rerun()

    # ------------------------------------------------------ remise & arrondi
    with st.container(border=True):
        st.markdown('<div class="sec" style="margin-top:0">Ajustements</div>', unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        mode_remise = r1.selectbox("Type de remise", ["Aucune", "Montant (DZD)", "Pourcentage"],
                                   key="mode_remise_%d" % doc_id,
                                   index=1 if remise else 0)
        if mode_remise == "Montant (DZD)":
            remise = r2.number_input("Remise", min_value=0.0, step=500.0, value=float(remise),
                                     key="remise_m_%d" % doc_id)
        elif mode_remise == "Pourcentage":
            taux = r2.number_input("Remise %", min_value=0.0, max_value=100.0, step=1.0,
                                   value=round(remise / brut * 100, 1) if brut else 0.0,
                                   key="remise_p_%d" % doc_id)
            remise = brut * taux / 100
        else:
            remise = 0.0
        total = max(0.0, brut - remise)

        a1, a2 = st.columns(2)
        if a1.button("Arrondir le total au millier", use_container_width=True):
            cible = arrondi_commercial(total, 1000)
            remise = max(0.0, brut - cible)
            _sauver(doc_id, lignes, remise)
            c.toast("Total arrondi \u00e0 %s" % dz(cible))
            st.rerun()
        acompte_pct = db.get_param_num("acompte_defaut", 50)
        a2.markdown('<div class="sm muted" style="padding-top:10px">Acompte conseill\u00e9 : '
                    '<b>%s</b> (%d %%)</div>' % (dz(total * acompte_pct / 100), int(acompte_pct)),
                    unsafe_allow_html=True)

    # ------------------------------------------------------ barre d'action
    with st.container(border=False, key="barre_action"):
        st.markdown('<div style="display:flex;justify-content:space-between;align-items:baseline">'
                    '<span class="sm muted">Total client \u00b7 sans TVA</span>'
                    '<span class="money" style="font-size:24px">%s</span></div>' % dz(total),
                    unsafe_allow_html=True)
        b1, b2, b3 = st.columns([1, 1, 1.2])
        if b1.button(c.bi("\U0001f4be \u062d\u0641\u0638", "Enregistrer"), use_container_width=True):
            _sauver(doc_id, lignes, remise)
            st.session_state["etape_devis"] = 1
            c.toast("Devis enregistr\u00e9")
            st.rerun()
        if b2.button("\U0001f4c4 PDF", use_container_width=True):
            _sauver(doc_id, lignes, remise)
            chemin = pdf.generer(doc_id)
            with open(chemin, "rb") as fichier:
                st.session_state["pdf_pret"] = {"doc": doc_id, "nom": os.path.basename(chemin),
                                                "donnees": fichier.read()}
        if b3.button(c.bi("\U0001f4f2 \u0625\u0631\u0633\u0627\u0644", "Envoyer"), type="primary",
                     use_container_width=True):
            _sauver(doc_id, lignes, remise)
            st.session_state["dialog_envoi"] = doc_id
            st.rerun()

    pret = st.session_state.get("pdf_pret")
    if pret and pret.get("doc") == doc_id:
        with st.container(border=True):
            tele, fermer = st.columns([4, 1])
            tele.download_button(c.bi("\u2b07\ufe0f \u062a\u062d\u0645\u064a\u0644", "T\u00e9l\u00e9charger") + "  " + pret["nom"],
                                 pret["donnees"], file_name=pret["nom"], mime="application/pdf",
                                 use_container_width=True, type="primary", key="dl_pdf_%d" % doc_id)
            if fermer.button("\u2715", key="pdf_fermer_%d" % doc_id, use_container_width=True):
                st.session_state.pop("pdf_pret", None)
                st.rerun()
            st.caption(c.bi("\u0627\u0644\u0640 PDF \u062c\u0627\u0647\u0632: \u0623\u0631\u0633\u0644\u0647 \u0639\u0628\u0631 WhatsApp \u0623\u0648 Viber \u0645\u0646 \u0647\u0627\u062a\u0641\u0643",
                            "Le PDF est pr\u00eat : envoyez-le par WhatsApp ou Viber."))

    if st.session_state.get("dialog_envoi") == doc_id:
        _dialog_envoi(doc_id)


# ==========================================================================
#  DIALOGUES SECONDAIRES
# ==========================================================================
@c.dialogue(c.bi("\u0645\u0643\u062a\u0628\u0629 \u0627\u0644\u0623\u0633\u0639\u0627\u0631", "Biblioth\u00e8que de prix"))
def _dialog_bibliotheque(lignes):
    st.caption("Vos prestations d\u00e9j\u00e0 vendues, avec le dernier prix pratiqu\u00e9.")
    recherche = st.text_input("Rechercher", key="biblio_rech", label_visibility="collapsed",
                              placeholder="\U0001f50e Rechercher une prestation\u2026")
    resultats = catalog.bibliotheque(recherche)
    if not resultats:
        c.vide("\U0001f4da", "Biblioth\u00e8que vide pour l'instant",
               "Chaque devis enregistr\u00e9 alimente automatiquement vos prix.")
    for row in resultats:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            col1.markdown('<div class="nm">%s</div><div class="ds">%s \u00b7 utilis\u00e9 %d fois</div>'
                          % (c.e(row["libelle"]), c.e(row["unite"]), row["usages"]),
                          unsafe_allow_html=True)
            col2.markdown('<div style="text-align:right" class="money">%s</div>'
                          % nombre(row["prix_unitaire"]), unsafe_allow_html=True)
            if st.button("Ajouter au devis", key="bib_%d" % row["id"], use_container_width=True):
                ligne = catalog.ligne_vide(row["libelle"], row["unite"], 1, row["prix_unitaire"],
                                           row["cout_materiaux"], row["cout_pose"])
                ligne["uid"] = uuid.uuid4().hex[:8]
                lignes.append(ligne)
                st.session_state["dialog_biblio"] = False
                st.session_state["grid_v"] = st.session_state.get("grid_v", 0) + 1
                st.rerun()
    if st.button("Fermer", use_container_width=True):
        st.session_state["dialog_biblio"] = False
        st.rerun()


@c.dialogue(c.bi("\u0625\u0631\u0633\u0627\u0644 \u0644\u0644\u0632\u0628\u0648\u0646", "Envoyer au client"))
def _dialog_envoi(doc_id):
    doc = docs.charger_document(doc_id)
    texte = message_devis(doc)
    texte = st.text_area("Message", value=texte, height=160, key="msg_envoi_%d" % doc_id)
    tel = doc.get("tel") or ""
    if not tel:
        st.warning("Ce client n'a pas de num\u00e9ro : ajoutez-le dans la fiche client "
                   "pour activer WhatsApp et Viber.")
    col1, col2 = st.columns(2)
    with col1:
        c.bouton_lien("WhatsApp", lien_whatsapp(tel, texte), "\U0001f4ac", "wa_%d" % doc_id, "primary")
    with col2:
        c.bouton_lien("Viber", lien_viber(tel, texte), "\U0001f4de", "vi_%d" % doc_id)
    st.caption(c.bi("\U0001f4ce \u0627ل\u0640 PDF: \u0627\u0636\u063a\u0637 \u0632\u0631 \u00ab PDF \U0001f4c4 \u00bb \u0641\u064a \u0635\u0641\u062d\u0629 \u0627\u0644\u0639\u0631\u0636 \u0644\u062a\u062d\u0645\u064a\u0644\u0647 \u062b\u0645 \u0623\u0631\u0633\u0644\u0647 \u0645\u0639 \u0627\u0644\u0631\u0633\u0627\u0644ة",
                    "Le PDF se t\u00e9l\u00e9charge depuis la page du devis (bouton \u00ab PDF \u00bb) : "
                    "cette fen\u00eatre reste ouverte."))
    if st.button("Marquer comme envoy\u00e9 et fermer", type="primary", use_container_width=True):
        if (doc.get("statut") or "") == "Brouillon":
            docs.changer_statut(doc_id, "Envoye")
        st.session_state.pop("dialog_envoi", None)
        st.rerun()
    if st.button("Fermer", use_container_width=True, key="fermer_envoi"):
        st.session_state.pop("dialog_envoi", None)
        st.rerun()
