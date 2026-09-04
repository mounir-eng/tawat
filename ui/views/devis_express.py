# -*- coding: utf-8 -*-
"""عرض سعر مباشر — Devis Express v9.

Trois écrans, un seul objectif : sortir un devis propre en 2 minutes.

  ① الزبون : nom + WhatsApp + type de bâtiment + MODE DE PRIX
              (Pose seulement  /  Pose et fourniture)
  ② القطع  : étage par étage. Sur chaque tuile on règle le NOMBRE de pièces
              avec un compteur, on ajoute TOUT d'un seul coup, la liste se pose
              en dessous, puis on personnalise chaque pièce (icône, nom, surface,
              tableau NF C 15-100 filtré par métier, câblage compris).
  ③ الملخص : total, remise, PDF, envoi WhatsApp.

Règle d'état Streamlit : on ne modifie JAMAIS la clé d'un widget après son
affichage. Les valeurs par défaut passent par des clés versionnées « _v<n> ».
"""
import os

import pandas as pd
import streamlit as st

from core import db, docs, nfc, pdf
from core.fmt import arrondi_commercial, lien_whatsapp, nombre, tel_international
from core.metier import UNITES, recalcul_total
from .. import components as c

# ------------------------------------------------------------------ constantes
MODES = [
    ("pose", "\U0001f527", "التركيب فقط", "Pose seulement",
     "الزبون يجيب القطع — العرض يحتوي على سعر اليد العاملة فقط."),
    ("pose_fourniture", "\U0001f4e6", "التركيب مع القطع", "Pose et fourniture",
     "أنت تجيب القطع — يزيد عمود «سعر القطعة» في الجدول."),
]

# Palette d'icônes (emoji classiques, rendus par toutes les versions de Windows).
ICONES = [
    "\U0001f6cb\ufe0f", "\U0001f6cf\ufe0f", "\U0001f476", "\U0001f373",
    "\U0001f6c1", "\U0001f6bd", "\U0001f6aa", "\u2b06\ufe0f", "\U0001f33f",
    "\u2600\ufe0f", "\U0001f697", "\U0001f4bc", "\U0001f5a5\ufe0f", "\u26a1",
    "\u2699\ufe0f", "\U0001f527", "\U0001f4e6", "\U0001f3ea",
    "\U0001f6bb", "\U0001f4a7",
]

MAX_PAR_TYPE = 12


# ================================================================== état
def _vider(cle):
    """Vide un widget si pre_clear_<cle> a été posé (à appeler AVANT le widget)."""
    if st.session_state.pop("pre_clear_" + cle, False):
        st.session_state.pop(cle, None)


def _aller(etape):
    st.session_state["dx_etape"] = etape
    st.rerun()


def _pieces():
    return st.session_state.setdefault("dx_pieces", [])


def _mode():
    return st.session_state.get("dx_mode") or "pose"


def _avec_fourniture():
    return _mode() == "pose_fourniture"


def _bat():
    return st.session_state.get("dx_batiment")


def _num(valeur, defaut=0.0):
    try:
        if valeur is None or (isinstance(valeur, float) and pd.isna(valeur)):
            return defaut
        if isinstance(valeur, str) and not valeur.strip():
            return defaut
        return float(valeur)
    except (TypeError, ValueError):
        return defaut


def _total_piece(p):
    return sum(_num(l.get("quantite")) * _num(l.get("prix_unitaire"))
               for l in p.get("lignes", []))


def _total():
    return sum(_total_piece(p) for p in _pieces())


def _ordre_pieces():
    rang = {n: i for i, n in enumerate(nfc.ORDRE_NIVEAUX)}
    return sorted(_pieces(), key=lambda p: rang.get(p.get("niveau") or "", 99))


def _latin(txt):
    """Vrai si le texte est imprimable tel quel dans le PDF (pas d'arabe)."""
    return all(ord(ch) < 0x0590 for ch in txt or "")


def _remise_a_zero():
    for cle in [k for k in list(st.session_state.keys()) if str(k).startswith("dx_")]:
        st.session_state.pop(cle, None)


def _a_personnaliser():
    return [i for i, p in enumerate(_pieces()) if not p.get("perso")]


# ================================================================== tuiles
def _classe_nom(texte):
    """Le libellé rétrécit tout seul quand il est long : les tuiles restent égales."""
    taille = len(texte or "")
    if taille > 19:
        return "nm xs"
    if taille > 12:
        return "nm sm"
    return "nm"


def _tuile(icone, nom_ar, nom_fr):
    """En-tête de tuile : icône au gabarit fixe + libellés à taille adaptative."""
    c.html_bloc('<div class="dx-t"><div class="ico">%s</div>'
                '<div class="%s">%s</div><div class="fr">%s</div></div>'
                % (c.e(icone or "\u2795"), _classe_nom(nom_ar), c.e(nom_ar or ""),
                   c.e(nom_fr or "")))


# ================================================================== écran principal
def afficher():
    etape = st.session_state.setdefault("dx_etape", 1)
    _fil(etape)
    if etape >= 3:
        _etape_resume()
    elif etape == 2:
        _etape_pieces()
    else:
        _etape_client()


def _fil(etape):
    """Rail de progression + total vivant."""
    pas = [("الزبون", "Client"), ("القطع", "Pièces"), ("الإرسال", "Envoi")]
    cellules = ""
    for i, (ar, fr) in enumerate(pas, start=1):
        classe = "on" if i == etape else ("ok" if i < etape else "")
        puce = "\u2713" if i < etape else str(i)
        cellules += ('<div class="dx-st %s"><i>%s</i><b>%s</b><span>%s</span></div>'
                     % (classe, puce, c.e(ar), c.e(fr)))
    total = _total()
    droite = ""
    if total:
        droite = ('<div class="dx-rail-tot"><span>المجموع</span>'
                  '<b>%s<small>DZD</small></b></div>' % nombre(total))
    c.html_bloc('<div class="dx-rail">%s%s</div>' % (cellules, droite))


# ================================================================== ① client
def _etape_client():
    c.entete(c.bi("عرض سعر جديد", "Nouveau devis"),
             c.bi("الزبون، نوع البناية، وطريقة التسعير",
                  "Client, type de bâtiment et mode de prix"))

    c.html_bloc('<div class="dx-lab"><i>1</i>معلومات الزبون'
                '<small>Coordonnées du client</small></div>')
    with st.container(key="dx_client"):
        gauche, droite = st.columns([1.25, 1])
        _vider("dx_nom")
        _vider("dx_tel")
        gauche.text_input(c.bi("اسم الزبون", "Nom du client"), key="dx_nom",
                          placeholder="Ex : Ammi Salah")
        droite.text_input(c.bi("رقم واتساب", "Numéro WhatsApp"), key="dx_tel",
                          placeholder="05 55 12 34 56")

    c.html_bloc('<div class="dx-lab"><i>2</i>نوع البناية'
                '<small>Type de bâtiment</small></div>')
    with st.container(key="dx_bats"):
        cles = list(nfc.ORDRE_BATIMENTS)
        for depart in range(0, len(cles), 4):
            colonnes = st.columns(4)
            for col, cle in zip(colonnes, cles[depart:depart + 4]):
                info = nfc.TYPES_BATIMENT[cle]
                actif = _bat() == cle
                with col:
                    with st.container(key="dxbox_%s%s" % ("on_" if actif else "", cle)):
                        _tuile(info["icone"], info["ar"], info["fr"])
                        libelle = "\u2713 مختار" if actif else "اختيار"
                        if st.button(libelle, key="dxb_%s" % cle,
                                     use_container_width=True,
                                     type="primary" if actif else "secondary"):
                            st.session_state["dx_batiment"] = cle
                            st.session_state.pop("dx_niv_pills", None)
                            st.rerun()

    c.html_bloc('<div class="dx-lab"><i>3</i>طريقة التسعير'
                '<small>Pose seulement ou pose + fourniture</small></div>')
    with st.container(key="dx_modes"):
        colonnes = st.columns(2)
        for col, (cle, icone, ar, fr, aide) in zip(colonnes, MODES):
            actif = _mode() == cle
            with col:
                with st.container(key="dxbox_m%s_%s" % ("_on" if actif else "", cle)):
                    _tuile(icone, ar, fr)
                    st.markdown('<div class="dx-modehelp">%s</div>' % c.e(aide),
                                unsafe_allow_html=True)
                    libelle = "\u2713 مختار" if actif else "اختيار"
                    if st.button(libelle, key="dxm_%s" % cle, use_container_width=True,
                                 type="primary" if actif else "secondary"):
                        st.session_state["dx_mode"] = cle
                        st.rerun()

    if _avec_fourniture():
        c.html_bloc('<div class="dx-note">\U0001f4e6 عمود <b>سعر القطعة</b> يزيد في '
                    'كل جدول، والمجموع يحسب: سعر القطعة + سعر التركيب.</div>')

    pret = bool((st.session_state.get("dx_nom") or "").strip()) and bool(_bat())
    with st.container(key="barre_action"):
        if _pieces():
            c.html_bloc('<div class="dx-barre-tot"><span>%d قطعة محفوطة</span><b>%s '
                        '<small>DZD</small></b></div>' % (len(_pieces()), nombre(_total())))
        if st.button(c.bi("التالي: القطع والأعمال \u203a", "Suivant : pièces et travaux"),
                     key="dx_go2", type="primary", use_container_width=True,
                     disabled=not pret):
            _aller(2)
        if not pret:
            st.caption(c.bi("اكتب اسم الزبون واختر نوع البناية للمتابعة.",
                            "Saisissez le nom du client et choisissez le bâtiment."))


def _client_id(nom, tel):
    """Retrouve le client par numéro (ou nom), sinon le crée."""
    existant = None
    if tel:
        existant = db.one(
            "SELECT * FROM clients WHERE replace(replace(telephone,' ',''),'-','')=?",
            (tel.replace(" ", "").replace("-", ""),))
    if not existant:
        existant = db.one("SELECT * FROM clients WHERE nom=?", (nom,))
    if existant:
        if tel and not (existant.get("telephone") or "").strip():
            db.run("UPDATE clients SET telephone=? WHERE id=?", (tel, existant["id"]))
        return existant["id"]
    return db.run("INSERT INTO clients (nom,telephone) VALUES (?,?)", (nom, tel))


# ================================================================== ② pièces
def _etape_pieces():
    bat = _bat()
    if not bat:
        _aller(1)
        return
    info = nfc.TYPES_BATIMENT[bat]
    nom_client = (st.session_state.get("dx_nom") or "").strip() or "\u2014"
    mode_lib = "التركيب مع القطع" if _avec_fourniture() else "التركيب فقط"

    c.entete("%s %s" % (info["icone"], info["ar"]),
             c.bi("الزبون: %s", "Client : %s", nom_client),
             pilule_droite=c.pilule(mode_lib, "blue" if _avec_fourniture() else "grey"))

    if st.button(c.bi("\u2039 رجوع للمعلومات", "< Informations client"), key="dx_back1"):
        _aller(1)

    # ------------------------------------------------------------ étages
    niveaux = nfc.niveaux_batiment(bat)
    niveau = ""
    if niveaux:
        c.html_bloc('<div class="dx-lab"><i>\U0001f3e2</i>الطابق'
                    '<small>Chaque étage est chiffré séparément</small></div>')
        libelles = ["%s %s" % (nfc.icone_niveau(n), nfc.nom_niveau(n, "ar")) for n in niveaux]
        defaut = libelles[niveaux.index("rdc")] if "rdc" in niveaux else libelles[0]
        choix = c.pilules_filtre("etage", libelles, "dx_niv_pills", defaut=defaut)
        niveau = niveaux[libelles.index(choix)] if choix in libelles else "rdc"
        st.session_state["dx_niveau"] = niveau

    # ------------------------------------------------------------ ajout / personnalisation
    if st.session_state.get("dx_ajout"):
        _panneau()
    else:
        _selecteur(bat, niveau)

    # ------------------------------------------------------------ pièces ajoutées
    liste = _ordre_pieces()
    if not liste:
        c.vide("\U0001f4d0", c.bi("لا توجد قطع بعد", "Aucune pièce"),
               c.bi("حدد العدد فوق كل قطعة ثم اضغط زر الإضافة مرة واحدة.",
                    "Réglez le nombre sur les tuiles puis ajoutez tout d'un coup."))
    else:
        c.section(c.bi("القطع المضافة (%d)", "Pièces ajoutées (%d)", len(liste)))
        restant = _a_personnaliser()
        if restant:
            c.html_bloc('<div class="dx-hint">\U0001f449 بقيت <b>%d</b> قطعة للتخصيص: '
                        'اضغط <b>تخصيص</b> لتغيير الأيقونة، الاسم، المساحة والأعمال.</div>'
                        % len(restant))
        dernier = None
        for p in liste:
            if niveaux and p.get("niveau") != dernier:
                dernier = p.get("niveau")
                total_niv = sum(_total_piece(x) for x in liste if x.get("niveau") == dernier)
                c.html_bloc('<div class="dx-flr"><b>%s %s</b><span>%s DZD</span></div>'
                            % (nfc.icone_niveau(dernier),
                               c.e(nfc.nom_niveau(dernier, "ar")), nombre(total_niv)))
            _carte_piece(_pieces().index(p), p)

    # ------------------------------------------------------------ barre d'action
    with st.container(key="barre_action"):
        c.html_bloc('<div class="dx-barre-tot"><span>%s</span><b>%s <small>DZD</small></b></div>'
                    % (c.e("المجموع بدون رسوم"), nombre(_total())))
        if st.button(c.bi("حفط العرض والانتقال للإرسال", "Enregistrer et envoyer"),
                     key="dx_save", type="primary", use_container_width=True,
                     disabled=not _pieces()):
            _sauver()


def _selecteur(bat, niveau):
    """Grille de tuiles avec compteur : on ajoute toutes les pièces d'un seul coup."""
    titre = "أضف القطع وعددها"
    if niveau:
        titre = "أضف القطع إلى %s" % nfc.nom_niveau(niveau, "ar")
    c.html_bloc('<div class="dx-lab"><i>+</i>%s<small>Réglez le nombre, ajoutez tout '
                'd\'un coup</small></div>' % c.e(titre))

    cles = nfc.pieces_batiment(bat)
    if not cles:
        st.info(c.bi("لا توجد قطع مقترحة لهذا النوع.", "Aucune pièce pour ce type."))
        return

    with st.container(key="dx_pcs"):
        for depart in range(0, len(cles), 4):
            colonnes = st.columns(4)
            for col, cle in zip(colonnes, cles[depart:depart + 4]):
                p = nfc.PIECES[cle]
                champ = "dxn_%s" % cle
                _vider(champ)
                if champ not in st.session_state:
                    st.session_state[champ] = 0
                choisi = int(_num(st.session_state.get(champ), 0))
                with col:
                    with st.container(key="dxtile_%s%s" % ("on_" if choisi else "", cle)):
                        _tuile(p["icone"], p["ar"], p["fr"])
                        st.number_input("العدد", min_value=0, max_value=MAX_PAR_TYPE,
                                        step=1, key=champ, label_visibility="collapsed")

    demandes = []
    for cle in cles:
        nb = int(_num(st.session_state.get("dxn_%s" % cle), 0))
        if nb > 0:
            demandes.append((cle, nb))
    total_sel = sum(nb for _cle, nb in demandes)

    if demandes:
        apercu = " \u00b7 ".join("%s %s \u00d7%d" % (nfc.PIECES[cle]["icone"],
                                                    nfc.PIECES[cle]["ar"], nb)
                                 for cle, nb in demandes)
        c.html_bloc('<div class="dx-lot"><b>%d</b><span>%s</span></div>'
                    % (total_sel, c.e(apercu)))

    with st.container(key="dx_addbar"):
        if st.button(c.bi("\u2795 أضف القطع المحددة (%d)", "Ajouter les %d pièces",
                          total_sel),
                     key="dx_addlot", type="primary", use_container_width=True,
                     disabled=not demandes):
            _ajouter_lot(bat, niveau, demandes)


def _modele_norme(bat, cle, surface, avec):
    """Postes proposés par la norme, prêts à devenir des lignes de devis."""
    modele = []
    for s in nfc.suggestions(bat, cle, surface, avec):
        pose = _num(s.get("prix_pose"), _num(s.get("prix_unitaire")))
        modele.append({"ok": bool(s.get("obligatoire", True)), "libelle": s["libelle"],
                       "unite": s.get("unite") or "U", "qte": _num(s.get("quantite")),
                       "pose": pose,
                       "fourn": _num(s.get("prix_fourniture")) if avec else 0.0,
                       "qte_ref": _num(s.get("quantite"))})
    return modele


def _ajouter_lot(bat, niveau, demandes):
    """Crée d'un seul coup toutes les pièces demandées, déjà chiffrées."""
    avec = _avec_fourniture()
    ajoutees = 0
    for cle, nb in demandes:
        info = nfc.PIECES.get(cle) or {"ar": cle, "fr": cle, "icone": "", "surface": 12}
        surface = float(info.get("surface") or 0)
        modele = _modele_norme(bat, cle, surface, avec)
        lignes = _lignes_instance(bat, cle, surface, avec, modele)
        base_fr = nfc.nom_piece(cle, "fr") or cle
        deja = sum(1 for p in _pieces()
                   if p.get("cle") == cle and (p.get("niveau") or "") == (niveau or ""))
        plusieurs = (deja + int(nb)) > 1
        for i in range(int(nb)):
            rang = deja + i + 1
            titre = ("%s %d" % (info["ar"], rang)) if plusieurs else info["ar"]
            etiquette = ("%s %d" % (base_fr, rang)) if plusieurs else base_fr
            if niveau:
                etiquette = "%s / %s" % (nfc.nom_niveau(niveau, "fr"), etiquette)
            _pieces().append({"cle": cle, "niveau": niveau or "", "icone": "",
                              "titre": titre, "nom": etiquette, "surface": surface,
                              "perso": False,
                              "lignes": [dict(l) for l in lignes]})
            ajoutees += 1
        st.session_state["pre_clear_dxn_%s" % cle] = True
    c.toast(c.bi("\u2705 أُضيفت %d قطعة — خصّص كل واحدة", "%d pièces ajoutées",
                 ajoutees), "\u2705")
    st.rerun()


def _carte_piece(index, p):
    icone = p.get("icone") or nfc.PIECES.get(p["cle"], {}).get("icone", "\U0001f4cc")
    detail = "%d عمل" % len(p.get("lignes", []))
    if p.get("surface"):
        detail += " \u00b7 %s m\u00b2" % nombre(p["surface"])
    if p.get("niveau"):
        detail += " \u00b7 %s" % nfc.nom_niveau(p["niveau"], "ar")
    badge = ('<span class="bg ok">\u2713 مخصّصة</span>' if p.get("perso")
             else '<span class="bg">بانتطار التخصيص</span>')
    c.html_bloc('<div class="dx-piece"><div class="ico">%s</div>'
                '<div class="mid"><div class="nm">%s</div><div class="ds">%s</div>%s</div>'
                '<div class="tot">%s<small>DZD</small></div></div>'
                % (c.e(icone), c.e(p.get("titre") or p.get("nom") or ""), c.e(detail),
                   badge, nombre(_total_piece(p))))
    gauche, milieu, _reste = st.columns([1.25, 1, 3])
    if gauche.button(c.bi("\u2699\ufe0f تخصيص", "Personnaliser"), key="dxe_%d" % index,
                     use_container_width=True,
                     type="secondary" if p.get("perso") else "primary"):
        _ouvrir(p["cle"], p.get("niveau") or "", index)
    if milieu.button(c.bi("حذف", "Supprimer"), key="dxd_%d" % index,
                     use_container_width=True):
        _pieces().pop(index)
        st.rerun()


def _ouvrir(cle, niveau, index):
    """Ouvre le panneau de personnalisation (ajout ou modification)."""
    st.session_state["dx_ajout"] = {"cle": cle, "niveau": niveau or "", "index": index}
    st.session_state["dx_v"] = st.session_state.get("dx_v", 0) + 1
    st.session_state.pop("dx_sig", None)
    st.session_state.pop("dx_base", None)
    st.rerun()


def _fermer():
    st.session_state.pop("dx_ajout", None)
    st.session_state.pop("dx_sig", None)
    st.session_state.pop("dx_base", None)
    st.rerun()


def _panneau():
    """Panneau intégré (pas de fenêtre) : icône, nom, surface, tableau des postes."""
    a = st.session_state["dx_ajout"]
    cle, niveau, index = a["cle"], a.get("niveau") or "", a.get("index")
    edition = index is not None and index < len(_pieces())
    info = nfc.PIECES.get(cle) or {"ar": cle, "fr": cle, "icone": "", "surface": 12}
    bat = _bat()
    avec = _avec_fourniture()
    v = st.session_state.get("dx_v", 0)
    origine = _pieces()[index] if edition else {}

    with st.container(key="dx_panel"):
        chapeau = nfc.nom_niveau(niveau, "ar") if niveau else ""
        c.html_bloc('<div class="dx-phead"><b>%s %s</b>%s</div>'
                    % (info["icone"], c.e(origine.get("titre") or info["ar"]),
                       ('<span>%s</span>' % c.e(chapeau)) if chapeau else ""))

        # ---------------------------------------------------- icône personnalisée
        cle_ic = "dx_ic_%s_v%d" % (cle, v)
        if cle_ic not in st.session_state:
            st.session_state[cle_ic] = origine.get("icone", "") if edition else ""
        icone = st.session_state.get(cle_ic) or ""

        box, ident, nb_col, surf_col = st.columns([0.8, 2.2, 1.05, 1.05])
        box.markdown('<div class="dx-icobox %s">%s</div>'
                     % ("" if icone else "vide", icone or "+"), unsafe_allow_html=True)
        nom = ident.text_input(c.bi("اسم القطعة", "Nom de la pièce"),
                               value=origine.get("titre") if edition else info["ar"],
                               key="dx_nomp_%s_v%d" % (cle, v))
        nb = 1
        if not edition:
            nb = int(nb_col.number_input(c.bi("عدد القطع", "Nombre"), min_value=1,
                                         max_value=MAX_PAR_TYPE, value=1, step=1,
                                         key="dx_nb_%s_v%d" % (cle, v)))
        else:
            nb_col.markdown('<div class="dx-fix">%s</div>' % c.e("تخصيص قطعة واحدة"),
                            unsafe_allow_html=True)
        surface = float(surf_col.number_input(
            c.bi("المساحة m\u00b2", "Surface m\u00b2"), min_value=0.0,
            value=float(origine.get("surface") if edition else info.get("surface") or 0),
            step=1.0, key="dx_sf_%s_v%d" % (cle, v)))

        with st.expander(c.bi("\U0001f3a8 اختر أيقونة القطعة", "Choisir une icône"),
                         expanded=False):
            with st.container(key="dx_icones"):
                for depart in range(0, len(ICONES), 10):
                    colonnes = st.columns(10)
                    for col, emoji in zip(colonnes, ICONES[depart:depart + 10]):
                        if col.button(emoji, key="dxi_%s_%d_v%d"
                                      % (cle, ICONES.index(emoji), v),
                                      use_container_width=True):
                            st.session_state[cle_ic] = emoji
                            st.rerun()
            libre, vider = st.columns([2, 1])
            saisie = libre.text_input(c.bi("أو اكتب رمزًا / حرفًا", "Ou saisir un symbole"),
                                      value="", max_chars=3,
                                      key="dx_iclibre_%s_v%d" % (cle, v))
            if saisie and saisie.strip() and saisie.strip() != icone:
                st.session_state[cle_ic] = saisie.strip()
                st.rerun()
            if vider.button(c.bi("تفريغ", "Vider"), key="dx_icoff_%s_v%d" % (cle, v),
                            use_container_width=True):
                st.session_state[cle_ic] = ""
                st.rerun()

        # ---------------------------------------------------- noms individuels
        if nb > 1:
            c.html_bloc('<div class="dx-hint">سمِّ كل قطعة على حدة — مثال: '
                        '<b>2 للأطفال</b> و <b>1 للأهل</b>. كل قطعة لها مساحتها.</div>')
            for i in range(nb):
                col_nom, col_srf = st.columns([2.6, 1])
                col_nom.text_input(c.bi("القطعة %d", "Pièce %d", i + 1),
                                   value="%s %d" % (nom or info["ar"], i + 1),
                                   key="dx_np_%s_%d_v%d" % (cle, i, v),
                                   label_visibility="visible" if i == 0 else "collapsed")
                col_srf.number_input("m\u00b2", min_value=0.0, value=surface, step=1.0,
                                     key="dx_ns_%s_%d_v%d" % (cle, i, v),
                                     label_visibility="visible" if i == 0 else "collapsed")

        # ---------------------------------------------------- tableau des postes
        signature = ("e%s" % index) if edition else ("%s|%s|%.1f|%s"
                                                     % (bat, cle, surface, _mode()))
        if st.session_state.get("dx_sig") != signature:
            st.session_state["dx_sig"] = signature
            st.session_state["dx_tv"] = st.session_state.get("dx_tv", 0) + 1
            if edition:
                st.session_state["dx_base"] = [
                    {"libelle": l.get("description", ""), "unite": l.get("unite") or "U",
                     "quantite": _num(l.get("quantite")),
                     "prix_pose": _num(l.get("cout_pose")) or _num(l.get("prix_unitaire")),
                     "prix_fourniture": _num(l.get("cout_materiaux")),
                     "prix_unitaire": _num(l.get("prix_unitaire")),
                     "norme": "", "obligatoire": True, "metier": ""}
                    for l in origine.get("lignes", [])]
            else:
                st.session_state["dx_base"] = nfc.suggestions(bat, cle, surface, avec)
        base = st.session_state.get("dx_base") or []

        if not base:
            st.info(c.bi("لا توجد أعمال مقترحة لهذه القطعة في حرفتك.",
                         "Aucun poste proposé pour cette pièce dans votre métier."))

        ref, rangees = {}, []
        for s in base:
            pose = _num(s.get("prix_pose"), _num(s.get("prix_unitaire")))
            ref[s["libelle"]] = _num(s.get("quantite"))
            rangees.append({"ok": bool(s.get("obligatoire", True)),
                            "libelle": s["libelle"],
                            "qte": _num(s.get("quantite")),
                            "unite": s.get("unite") or "U",
                            "fourn": _num(s.get("prix_fourniture")),
                            "pose": pose})
        vues = ["ok", "libelle", "qte", "unite"] + (["fourn"] if avec else []) + ["pose"]
        cadre = pd.DataFrame(rangees, columns=["ok", "libelle", "qte", "unite",
                                               "fourn", "pose"])

        config = {
            "ok": st.column_config.CheckboxColumn(c.bi("ضمّن", "OK"), width="small"),
            "libelle": st.column_config.TextColumn(c.bi("الخدمة", "Désignation"),
                                                   width="large"),
            "qte": st.column_config.NumberColumn(c.bi("الكمية", "Qté"), min_value=0.0,
                                                 step=1.0, width="small"),
            "unite": st.column_config.SelectboxColumn(c.bi("الوحدة", "Unité"),
                                                      options=UNITES, width="small"),
            "pose": st.column_config.NumberColumn(c.bi("سعر التركيب", "Pose DZD"),
                                                  min_value=0.0, step=50.0),
        }
        if avec:
            config["fourn"] = st.column_config.NumberColumn(
                c.bi("سعر القطعة", "Fourniture DZD"), min_value=0.0, step=50.0)
        edite = st.data_editor(cadre[vues],
                               key="dxg_%s_v%d" % (cle, st.session_state.get("dx_tv", 0)),
                               hide_index=True, use_container_width=True,
                               num_rows="dynamic", column_config=config)

        modele, total_p = [], 0.0
        for _index, r in edite.iterrows():
            libelle = str(r.get("libelle") or "").strip()
            if not libelle or libelle.lower() == "nan":
                continue
            garde = bool(r.get("ok"))
            qte = _num(r.get("qte"))
            pose = _num(r.get("pose"))
            fourn = _num(r.get("fourn")) if avec else 0.0
            modele.append({"ok": garde, "libelle": libelle, "unite": r.get("unite") or "U",
                           "qte": qte, "pose": pose, "fourn": fourn,
                           "qte_ref": ref.get(libelle, qte)})
            if garde:
                total_p += qte * (pose + fourn)

        detail = ""
        if avec:
            mat = sum(m["qte"] * m["fourn"] for m in modele if m["ok"])
            detail = ('<span>منها قطع: %s \u00b7 تركيب: %s</span>'
                      % (nombre(mat), nombre(total_p - mat)))
        multiple = ('<span>\u00d7 %d قطعة = %s DZD</span>' % (nb, nombre(total_p * nb))) \
            if nb > 1 else ""
        c.html_bloc('<div class="dx-tot"><b>%s <small>DZD</small></b>%s%s</div>'
                    % (nombre(total_p), detail, multiple))

        justif = [s for s in base if s.get("norme")]
        if justif:
            with st.expander(c.bi("\U0001f4d8 لماذا هذه الأعمال؟ (NF C 15-100)",
                                  "Justification NF C 15-100")):
                for s in justif:
                    st.markdown("**%s** \u2014 %s" % (s["libelle"], s["norme"]))

        reste = [i for i in _a_personnaliser() if i != index]
        if edition and reste:
            valider, suite, annuler = st.columns([1.5, 1.5, 1])
        else:
            valider, annuler = st.columns([2, 1])
            suite = None
        if edition:
            libelle_ok = c.bi("\u2713 حفط التخصيص", "Enregistrer")
        elif nb > 1:
            libelle_ok = c.bi("إضافة %d قطع", "Ajouter %d pièces", nb)
        else:
            libelle_ok = c.bi("إضافة القطعة", "Ajouter la pièce")
        if valider.button(libelle_ok, key="dx_ok_%s_v%d" % (cle, v), type="primary",
                          use_container_width=True):
            _valider(cle, niveau, index, nom, icone, surface, nb, modele, avec, bat, v)
        if suite is not None and suite.button(
                c.bi("حفط والقطعة الموالية \u203a", "Enregistrer et suivante"),
                key="dx_next_%s_v%d" % (cle, v), use_container_width=True):
            _valider(cle, niveau, index, nom, icone, surface, nb, modele, avec, bat, v,
                     suivant=True)
        if annuler.button(c.bi("إلغاء", "Annuler"), key="dx_no_%s_v%d" % (cle, v),
                          use_container_width=True):
            _fermer()


def _lignes_instance(bat, cle, surface, avec, modele):
    """Lignes finales : quantités recalculées par la norme si non retouchées à la main."""
    sugg = {}
    if surface > 0:
        sugg = {s["libelle"]: s for s in nfc.suggestions(bat, cle, surface, avec)}
    lignes = []
    for m in modele:
        if not m["ok"]:
            continue
        qte = m["qte"]
        propose = sugg.get(m["libelle"])
        if propose is not None and abs(m["qte"] - _num(m.get("qte_ref"))) < 0.01:
            qte = _num(propose.get("quantite"), qte)
        fourn = m["fourn"] if avec else 0.0
        lignes.append({"description": m["libelle"], "quantite": qte,
                       "unite": m["unite"], "prix_unitaire": m["pose"] + fourn,
                       "cout_materiaux": fourn, "cout_pose": m["pose"]})
    return lignes


def _valider(cle, niveau, index, nom, icone, surface, nb, modele, avec, bat, v,
             suivant=False):
    if not any(m["ok"] for m in modele):
        st.warning(c.bi("اختر عملًا واحدًا على الأقل.", "Cochez au moins un poste."))
        return
    base_fr = nfc.nom_piece(cle, "fr") or cle
    nouvelles = []
    for i in range(max(1, int(nb))):
        titre = nom or nfc.nom_piece(cle, "ar")
        surf_i = surface
        if nb > 1:
            titre = (st.session_state.get("dx_np_%s_%d_v%d" % (cle, i, v)) or "").strip() \
                or "%s %d" % (titre, i + 1)
            surf_i = _num(st.session_state.get("dx_ns_%s_%d_v%d" % (cle, i, v)), surface)
        etiquette = titre if _latin(titre) else (
            "%s %d" % (base_fr, i + 1) if nb > 1 else base_fr)
        if niveau:
            etiquette = "%s / %s" % (nfc.nom_niveau(niveau, "fr"), etiquette)
        nouvelles.append({"cle": cle, "niveau": niveau, "icone": icone, "titre": titre,
                          "nom": etiquette, "surface": surf_i, "perso": True,
                          "lignes": _lignes_instance(bat, cle, surf_i, avec, modele)})
    if index is not None and index < len(_pieces()):
        ancienne = _pieces()[index]
        nouvelles[0]["nom"] = ancienne.get("nom") if not _latin(nouvelles[0]["titre"]) \
            else nouvelles[0]["nom"]
        _pieces()[index] = nouvelles[0]
    else:
        _pieces().extend(nouvelles)
    st.session_state.pop("dx_sig", None)
    st.session_state.pop("dx_base", None)
    cible = None
    if suivant:
        cible = next((i for i in _a_personnaliser()), None)
    if cible is not None:
        p = _pieces()[cible]
        st.session_state["dx_ajout"] = {"cle": p["cle"], "niveau": p.get("niveau") or "",
                                        "index": cible}
        st.session_state["dx_v"] = st.session_state.get("dx_v", 0) + 1
    else:
        st.session_state["dx_ajout"] = None
    c.toast(c.bi("تم الحفط", "Enregistré"))
    st.rerun()


# ================================================================== sauvegarde
def _sauver():
    nom = (st.session_state.get("dx_nom") or "").strip() or "Client"
    tel = (st.session_state.get("dx_tel") or "").strip()
    bat = _bat()
    avec = _avec_fourniture()
    client_id = _client_id(nom, tel)

    lignes = []
    for p in _ordre_pieces():
        for l in p.get("lignes", []):
            ligne = dict(l)
            ligne["piece"] = p.get("nom") or ""
            ligne["niveau"] = nfc.nom_niveau(p["niveau"], "fr") if p.get("niveau") else ""
            lignes.append(ligne)

    note = "%s \u00b7 %s" % (nfc.nom_batiment(bat, "fr"),
                             "Pose et fourniture" if avec else "Pose seulement")
    doc_id = docs.creer_document(client_id, None, "Devis", lignes, note)
    db.run("UPDATE devis_factures SET type_batiment=?, mode_prix=? WHERE id=?",
           (bat, _mode(), doc_id))
    recalcul_total(doc_id)
    st.session_state["dx_doc"] = doc_id
    st.session_state.pop("dx_pdf", None)
    _aller(3)


# ================================================================== ③ résumé
def _etape_resume():
    doc_id = st.session_state.get("dx_doc")
    doc = docs.charger_document(doc_id) if doc_id else None
    if not doc:
        _aller(2)
        return
    lignes = docs.charger_lignes(doc_id)
    brut = sum(_num(l["quantite"]) * _num(l["prix_unitaire"]) for l in lignes)
    fourniture = sum(_num(l["quantite"]) * _num(l.get("cout_materiaux")) for l in lignes)
    remise = _num(doc.get("remise"))
    avec = (doc.get("mode_prix") or "pose") == "pose_fourniture"
    client = db.one("SELECT * FROM clients WHERE id=?", (doc["client_id"],)) or {}

    c.entete(c.bi("عرض السعر جاهز", "Devis prêt"),
             "%s \u00b7 %s" % (doc["numero"] or "", client.get("nom") or ""),
             pilule_droite=c.pilule("التركيب مع القطع" if avec else "التركيب فقط",
                                    "blue" if avec else "grey"))

    cases = [("عدد الأعمال", str(len(lignes)), "#8FE3B4")]
    if avec:
        cases.append(("منها قطع", nombre(fourniture), "#FFD8B4"))
        cases.append(("منها تركيب", nombre(brut - fourniture), "#BFD8FF"))
    elif remise:
        cases.append(("تخفيض", nombre(remise), "#FFB4AC"))
    c.hero(c.bi("المجموع بدون رسوم", "Total sans TVA"),
           nombre(_num(doc["total"])), "DZD", cases=cases)

    # ------------------------------------------------------------ remise / arrondi
    with st.container(key="dx_remcard"):
        col_r, col_a = st.columns([1.4, 1])
        _vider("dx_remise")
        nouvelle = col_r.number_input(c.bi("تخفيض (DZD)", "Remise (DZD)"), min_value=0.0,
                                      value=float(remise), step=500.0, key="dx_remise")
        if abs(_num(nouvelle) - remise) > 0.4:
            db.run("UPDATE devis_factures SET remise=? WHERE id=?", (_num(nouvelle), doc_id))
            recalcul_total(doc_id)
            st.session_state.pop("dx_pdf", None)
            st.rerun()
        col_a.markdown('<div class="dx-fix">%s</div>' % c.e("تدوير المبلغ"),
                       unsafe_allow_html=True)
        if col_a.button(c.bi("تدوير", "Arrondir"), key="dx_arr", use_container_width=True):
            cible = arrondi_commercial(brut - remise)
            db.run("UPDATE devis_factures SET remise=? WHERE id=?",
                   (max(0.0, brut - cible), doc_id))
            recalcul_total(doc_id)
            st.session_state["pre_clear_dx_remise"] = True
            st.session_state.pop("dx_pdf", None)
            st.rerun()

    # ------------------------------------------------------------ détail
    c.section(c.bi("التفصيل", "Détail"))
    groupes = []
    for l in lignes:
        cle_g = (l.get("niveau") or "", l.get("piece") or "")
        if not groupes or groupes[-1][0] != cle_g:
            groupes.append((cle_g, []))
        groupes[-1][1].append(l)
    for (niv, piece), items in groupes:
        total_g = sum(_num(x["quantite"]) * _num(x["prix_unitaire"]) for x in items)
        chapeau = piece or niv or "\u2014"
        rangs = ""
        for x in items:
            rangs += ('<tr><td>%s</td><td>%s %s</td><td>%s</td><td>%s</td></tr>'
                      % (c.e(x["description"]), nombre(_num(x["quantite"])),
                         c.e(x["unite"] or ""), nombre(_num(x["prix_unitaire"])),
                         nombre(_num(x["quantite"]) * _num(x["prix_unitaire"]))))
        c.html_bloc('<div class="dx-grp"><div class="gh"><b>%s</b><span>%s DZD</span></div>'
                    '<table class="dx-tbl">%s</table></div>'
                    % (c.e(chapeau), nombre(total_g), rangs))

    # ------------------------------------------------------------ PDF + WhatsApp
    c.section(c.bi("الإرسال", "Envoi"))
    with st.container(key="dx_envoi"):
        col1, col2 = st.columns(2)
        if col1.button(c.bi("\U0001f4c4 توليد PDF", "Générer le PDF"), key="dx_pdfgo",
                       use_container_width=True, type="primary"):
            st.session_state["dx_pdf"] = pdf.generer(doc_id)
            st.rerun()
        chemin = st.session_state.get("dx_pdf")
        if chemin and os.path.exists(chemin):
            with open(chemin, "rb") as fichier:
                col2.download_button(c.bi("تحميل PDF", "Télécharger"), fichier.read(),
                                     file_name=os.path.basename(chemin),
                                     mime="application/pdf", key="dx_dl",
                                     use_container_width=True)
        else:
            col2.button(c.bi("تحميل PDF", "Télécharger"), disabled=True,
                        use_container_width=True, key="dx_dl_off")

        message = _message(doc, client)
        c.message_copiable(message)
        tel = tel_international(client.get("telephone") or "")
        if tel:
            c.bouton_lien(c.bi("إرسال واتساب", "Envoyer sur WhatsApp"),
                          lien_whatsapp(tel, message), "\U0001f4f2", "dx_wa", "primary")

    gauche, droite = st.columns(2)
    if gauche.button(c.bi("\u2039 تعديل القطع", "< Modifier les pièces"), key="dx_back2",
                     use_container_width=True):
        _aller(2)
    if droite.button(c.bi("عرض سعر جديد", "Nouveau devis"), key="dx_new",
                     use_container_width=True):
        _remise_a_zero()
        st.session_state["dx_etape"] = 1
        st.rerun()


def _message(doc, client):
    entreprise = db.get_param("entreprise_nom") or ""
    total = nombre(_num(doc["total"]))
    return ("السلام عليكم %s\n"
            "هذا عرض السعر رقم %s.\n"
            "المجموع: %s دج (بدون رسوم).\n"
            "%s\n"
            "Devis %s \u2014 total %s DZD. Merci de votre confiance."
            % (client.get("nom") or "", doc["numero"] or "", total, entreprise,
               doc["numero"] or "", total))
