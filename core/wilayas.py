# -*- coding: utf-8 -*-
"""الولايات · Référentiel des 58 wilayas d'Algérie.

Un seul format d'affichage dans toute l'application :
    [16] الجزائر - Alger
Le code (int) est ce qui est stocké en base ; le libellé n'est qu'un rendu.
"""

# (code, nom arabe, nom francais)
WILAYAS = [
    (1, "أدرار", "Adrar"),
    (2, "الشلف", "Chlef"),
    (3, "الأغواط", "Laghouat"),
    (4, "أم البواقي", "Oum El Bouaghi"),
    (5, "باتنة", "Batna"),
    (6, "بجاية", "Béjaïa"),
    (7, "بسكرة", "Biskra"),
    (8, "بشار", "Béchar"),
    (9, "البليدة", "Blida"),
    (10, "البويرة", "Bouira"),
    (11, "تمنراست", "Tamanrasset"),
    (12, "تبسة", "Tébessa"),
    (13, "تلمسان", "Tlemcen"),
    (14, "تيارت", "Tiaret"),
    (15, "تيزي وزو", "Tizi Ouzou"),
    (16, "الجزائر", "Alger"),
    (17, "الجلفة", "Djelfa"),
    (18, "جيجل", "Jijel"),
    (19, "سطيف", "Sétif"),
    (20, "سعيدة", "Saïda"),
    (21, "سكيكدة", "Skikda"),
    (22, "سيدي بلعباس", "Sidi Bel Abbès"),
    (23, "عنابة", "Annaba"),
    (24, "قالمة", "Guelma"),
    (25, "قسنطينة", "Constantine"),
    (26, "المدية", "Médéa"),
    (27, "مستغانم", "Mostaganem"),
    (28, "المسيلة", "M'Sila"),
    (29, "معسكر", "Mascara"),
    (30, "ورقلة", "Ouargla"),
    (31, "وهران", "Oran"),
    (32, "البيض", "El Bayadh"),
    (33, "إليزي", "Illizi"),
    (34, "برج بوعريريج", "Bordj Bou Arréridj"),
    (35, "بومرداس", "Boumerdès"),
    (36, "الطارف", "El Tarf"),
    (37, "تندوف", "Tindouf"),
    (38, "تيسمسيلت", "Tissemsilt"),
    (39, "الوادي", "El Oued"),
    (40, "خنشلة", "Khenchela"),
    (41, "سوق أهراس", "Souk Ahras"),
    (42, "تيبازة", "Tipaza"),
    (43, "ميلة", "Mila"),
    (44, "عين الدفلى", "Aïn Defla"),
    (45, "النعامة", "Naâma"),
    (46, "عين تموشنت", "Aïn Témouchent"),
    (47, "غرداية", "Ghardïa"),
    (48, "غليزان", "Relizane"),
    (49, "تيميمون", "Timimoun"),
    (50, "برج باجي مختار", "Bordj Badji Mokhtar"),
    (51, "أولاد جلال", "Ouled Djellal"),
    (52, "بني عباس", "Béni Abbès"),
    (53, "عين صالح", "In Salah"),
    (54, "عين قزام", "In Guezzam"),
    (55, "تقرت", "Touggourt"),
    (56, "جانت", "Djanet"),
    (57, "المغير", "El M'Ghair"),
    (58, "المنيعة", "El Meniaa"),
]

CODES = [w[0] for w in WILAYAS]
_PAR_CODE = {w[0]: w for w in WILAYAS}

VIDE = "[--] كل الولايات - Toutes les wilayas"
FORMAT = "[%02d] %s - %s"


def _entier(valeur):
    try:
        return int(str(valeur).strip())
    except (TypeError, ValueError):
        return None


def libelle(code, vide=VIDE):
    """Libelle d'option propre : "[16] ... - Alger". `None` -> option vide."""
    fiche = _PAR_CODE.get(_entier(code))
    if not fiche:
        return vide
    return FORMAT % (fiche[0], fiche[1], fiche[2])


LIBELLES = {code: libelle(code) for code in CODES}


def nom(code, langue="fr"):
    fiche = _PAR_CODE.get(_entier(code))
    if not fiche:
        return ""
    return fiche[1] if langue == "ar" else fiche[2]


def options(avec_vide=True):
    """Liste de codes prete pour st.selectbox (avec format_func=libelle)."""
    return ([None] if avec_vide else []) + list(CODES)


def code_depuis(valeur):
    """Retrouve un code depuis un libelle, un nom francais/arabe ou un nombre."""
    entier = _entier(valeur)
    if entier in _PAR_CODE:
        return entier
    texte = ("" if valeur is None else str(valeur)).strip()
    if not texte:
        return None
    if texte.startswith("["):
        fin = texte.find("]")
        if fin > 1:
            code = _entier(texte[1:fin])
            if code in _PAR_CODE:
                return code
    minuscule = texte.lower()
    for code, arabe, francais in WILAYAS:
        if minuscule == francais.lower() or texte == arabe:
            return code
    for code, arabe, francais in WILAYAS:
        if francais.lower() in minuscule or arabe in texte:
            return code
    return None


def rechercher(motif):
    """Wilayas dont le nom arabe ou francais contient `motif`."""
    motif = (motif or "").strip().lower()
    if not motif:
        return list(CODES)
    return [code for code, arabe, francais in WILAYAS
            if motif in francais.lower() or motif in arabe]
