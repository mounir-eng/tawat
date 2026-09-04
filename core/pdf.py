# -*- coding: utf-8 -*-
"""G\u00e9n\u00e9ration des PDF (devis, facture, re\u00e7u) \u2014 mise en page sobre et lisible.

Les polices DejaVu sont embarqu\u00e9es si elles sont pr\u00e9sentes dans assets/fonts,
ce qui permet les accents fran\u00e7ais sans bricolage latin-1.
"""
import os

from fpdf import FPDF

from . import db
from .fmt import date_fr, nombre, tel_joli
from .metier import ETAPES_LIB, total_paye

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")


def _dossier_sortie():
    """Dossier des PDF : celui du logiciel, sinon un dossier temporaire.

    Sur un hebergeur (Streamlit Cloud) le dossier du code peut etre en lecture
    seule : on bascule automatiquement pour que le PDF soit toujours produit.
    """
    import tempfile
    candidats = []
    force = os.environ.get("ARTISAN_EXPORTS")
    if force:
        candidats.append(force)
    candidats.append(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "exports"))
    candidats.append(os.path.join(tempfile.gettempdir(), "artisan_dz_exports"))
    for dossier in candidats:
        try:
            os.makedirs(dossier, exist_ok=True)
            temoin = os.path.join(dossier, ".ecriture")
            with open(temoin, "w") as fichier:
                fichier.write("ok")
            os.remove(temoin)
            return dossier
        except OSError:
            continue
    return tempfile.gettempdir()
ENCRE = (27, 36, 49)
GRIS = (125, 122, 117)
TRAIT = (230, 229, 227)
DOUX = (249, 248, 247)
BLEU = (39, 131, 222)
VERT = (70, 161, 113)

MENTIONS = {
    "Devis": "Devis gratuit et sans engagement \u2014 montants en dinars alg\u00e9riens, sans TVA.",
    "Facture": "Facture \u00e9tablie en dinars alg\u00e9riens, sans TVA.",
    "Recu": "Re\u00e7u de paiement \u2014 montants en dinars alg\u00e9riens, sans TVA.",
}
TITRES = {"Devis": "DEVIS", "Facture": "FACTURE", "Recu": "RE\u00c7U"}


class Document(FPDF):
    def __init__(self, unicode_ok):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.unicode_ok = unicode_ok
        self.pied = ""

    def police(self, style="", taille=10):
        if self.unicode_ok:
            self.set_font("DejaVu", style, taille)
        else:
            self.set_font("Helvetica", style, taille)

    def footer(self):
        self.set_y(-15)
        self.police("", 8)
        self.set_text_color(*GRIS)
        self.cell(0, 5, _t(self, self.pied), align="C")
        self.ln(4)
        self.cell(0, 5, "Page %d" % self.page_no(), align="C")


def _t(pdf, texte):
    """Adapte le texte si aucune police Unicode n'est disponible."""
    texte = texte or ""
    if pdf.unicode_ok:
        return texte
    remplacements = {"\u20ac": "EUR", "\u2014": "-", "\u2013": "-", "\u2019": "'",
                     "\u202f": " ", "\u00a0": " ", "\u2026": "..."}
    for a, b in remplacements.items():
        texte = texte.replace(a, b)
    return texte.encode("latin-1", "replace").decode("latin-1")


def _charger_polices(pdf):
    regular = os.path.join(ASSETS, "DejaVuSans.ttf")
    bold = os.path.join(ASSETS, "DejaVuSans-Bold.ttf")
    if os.path.exists(regular):
        try:
            pdf.add_font("DejaVu", "", regular)
            pdf.add_font("DejaVu", "B", bold if os.path.exists(bold) else regular)
            pdf.add_font("DejaVu", "I", regular)
            return True
        except Exception:
            return False
    return False


def generer(document_id, chemin=None):
    """Cr\u00e9e le PDF du document et retourne son chemin."""
    doc = db.one(
        "SELECT f.*, c.nom AS client, c.telephone AS tel, c.adresse AS adr_client, "
        "c.ville AS ville, ch.nom AS chantier, ch.adresse AS adr_chantier "
        "FROM devis_factures f "
        "LEFT JOIN clients c ON c.id = f.client_id "
        "LEFT JOIN chantiers ch ON ch.id = f.chantier_id WHERE f.id=?", (document_id,))
    if not doc:
        raise ValueError("Document introuvable")
    lignes = db.q("SELECT * FROM lignes_document WHERE document_id=? ORDER BY ordre, id", (document_id,))

    pdf = Document(False)
    pdf.unicode_ok = _charger_polices(pdf)
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.add_page()
    marge = 15
    largeur = 210 - 2 * marge

    entreprise = db.get_param("entreprise_nom") or "Mon entreprise"
    metier = db.get_param("entreprise_metier")
    tel = db.get_param("entreprise_tel")
    adresse = db.get_param("entreprise_adresse")
    pdf.pied = " \u00b7 ".join([x for x in [entreprise, tel_joli(tel), adresse] if x])

    # ---------------------------------------------------------------- bandeau
    pdf.set_fill_color(*ENCRE)
    pdf.rect(0, 0, 210, 34, style="F")
    pdf.set_xy(marge, 9)
    pdf.set_text_color(255, 255, 255)
    pdf.police("B", 17)
    pdf.cell(120, 8, _t(pdf, entreprise))
    pdf.set_xy(marge, 18)
    pdf.police("", 9.5)
    pdf.set_text_color(215, 220, 228)
    sous_titre = " \u00b7 ".join([x for x in [metier, tel_joli(tel) if tel else "", adresse] if x])
    pdf.cell(120, 6, _t(pdf, sous_titre))

    titre = TITRES.get(doc["type_doc"], "DOCUMENT")
    pdf.set_xy(210 - marge - 60, 9)
    pdf.police("B", 20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 9, _t(pdf, titre), align="R")
    pdf.set_xy(210 - marge - 60, 19)
    pdf.police("", 10)
    pdf.set_text_color(215, 220, 228)
    pdf.cell(60, 6, _t(pdf, doc["numero"] or ""), align="R")

    # ---------------------------------------------------------------- blocs info
    pdf.set_y(44)
    y0 = pdf.get_y()
    bloc = (largeur - 6) / 2

    pdf.set_fill_color(*DOUX)
    pdf.set_draw_color(*TRAIT)
    pdf.rect(marge, y0, bloc, 30, style="DF")
    pdf.rect(marge + bloc + 6, y0, bloc, 30, style="DF")

    pdf.set_xy(marge + 5, y0 + 4)
    pdf.police("B", 8)
    pdf.set_text_color(*GRIS)
    pdf.cell(bloc - 10, 4, _t(pdf, "CLIENT"))
    pdf.set_xy(marge + 5, y0 + 10)
    pdf.police("B", 11.5)
    pdf.set_text_color(*ENCRE)
    pdf.cell(bloc - 10, 5, _t(pdf, doc.get("client") or "\u2014"))
    pdf.set_xy(marge + 5, y0 + 16)
    pdf.police("", 9)
    pdf.set_text_color(*GRIS)
    infos_client = "\n".join([x for x in [tel_joli(doc.get("tel")) if doc.get("tel") else "",
                                          doc.get("adr_client") or ""] if x])
    pdf.multi_cell(bloc - 10, 4.5, _t(pdf, infos_client))

    x2 = marge + bloc + 11
    pdf.set_xy(x2, y0 + 4)
    pdf.police("B", 8)
    pdf.set_text_color(*GRIS)
    pdf.cell(bloc - 10, 4, _t(pdf, "CHANTIER & DATES"))
    pdf.set_xy(x2, y0 + 10)
    pdf.police("B", 11.5)
    pdf.set_text_color(*ENCRE)
    pdf.cell(bloc - 10, 5, _t(pdf, doc.get("chantier") or "\u2014"))
    pdf.set_xy(x2, y0 + 16)
    pdf.police("", 9)
    pdf.set_text_color(*GRIS)
    lignes_date = ["Date : " + date_fr(doc.get("date_doc"))]
    if doc["type_doc"] == "Devis":
        lignes_date.append("Validit\u00e9 : %d jours" % int(db.get_param_num("validite_devis", 30)))
    elif doc.get("echeance"):
        lignes_date.append("\u00c9ch\u00e9ance : " + date_fr(doc.get("echeance")))
    if doc.get("adr_chantier"):
        lignes_date.append(doc["adr_chantier"])
    pdf.multi_cell(bloc - 10, 4.5, _t(pdf, "\n".join(lignes_date)))

    # ---------------------------------------------------------------- tableau
    pdf.set_y(y0 + 38)
    cols = [95, 20, 22, 33]  # designation, qte, unite... total
    cols = [92, 18, 20, 30]
    entetes = ["D\u00c9SIGNATION", "QT\u00c9", "UNIT\u00c9", "P.U.", "TOTAL"]
    largeurs = [80, 16, 18, 30, 36]

    pdf.set_fill_color(*ENCRE)
    pdf.set_text_color(255, 255, 255)
    pdf.police("B", 8.5)
    for i, entete in enumerate(entetes):
        align = "L" if i == 0 else "R"
        pdf.cell(largeurs[i], 9, _t(pdf, entete), border=0, align=align, fill=True)
    pdf.ln(9)

    pdf.set_text_color(*ENCRE)
    total_brut = 0.0
    impair = False
    piece_courante = None
    for ligne in lignes:
        # ------------------------------------------------ bandeau de local/piece
        piece = (ligne.get("piece") or "").strip()
        if piece and piece != piece_courante:
            piece_courante = piece
            if pdf.get_y() + 10 > 258:
                pdf.add_page()
            y_sec = pdf.get_y()
            pdf.set_fill_color(240, 239, 237)
            pdf.rect(marge, y_sec, sum(largeurs), 8, style="F")
            pdf.set_xy(marge + 3, y_sec)
            pdf.police("B", 9)
            pdf.set_text_color(*ENCRE)
            pdf.cell(sum(largeurs) - 6, 8, _t(pdf, piece.upper()))
            pdf.ln(8)
            pdf.set_text_color(*ENCRE)
            impair = False

        qte = float(ligne["quantite"] or 0)
        pu = float(ligne["prix_unitaire"] or 0)
        montant = qte * pu
        total_brut += montant
        texte = ligne["description"] or ""

        pdf.police("", 9.5)
        hauteur_texte = pdf.get_string_width(_t(pdf, texte))
        nb_lignes = max(1, int(hauteur_texte / (largeurs[0] - 4)) + 1)
        h = 6 * nb_lignes
        if pdf.get_y() + h > 260:
            pdf.add_page()
        y = pdf.get_y()
        if impair:
            pdf.set_fill_color(*DOUX)
            pdf.rect(marge, y, sum(largeurs), h, style="F")
        impair = not impair

        pdf.set_xy(marge, y)
        pdf.multi_cell(largeurs[0], 6, _t(pdf, texte), align="L")
        pdf.set_xy(marge + largeurs[0], y)
        pdf.cell(largeurs[1], h, _t(pdf, nombre(qte, 0 if qte == int(qte) else 2)), align="R")
        pdf.cell(largeurs[2], h, _t(pdf, ligne["unite"] or ""), align="R")
        pdf.cell(largeurs[3], h, _t(pdf, nombre(pu)), align="R")
        pdf.police("B", 9.5)
        pdf.cell(largeurs[4], h, _t(pdf, nombre(montant)), align="R")
        pdf.ln(h)
        pdf.set_draw_color(*TRAIT)
        pdf.line(marge, pdf.get_y(), marge + sum(largeurs), pdf.get_y())

    # ---------------------------------------------------------------- totaux
    remise = float(doc.get("remise") or 0)
    total = max(0.0, total_brut - remise)
    paye = total_paye(document_id)
    reste = max(0.0, total - paye)

    pdf.ln(6)
    x_tot = marge + sum(largeurs) - 86
    def ligne_total(libelle, valeur, gras=False, couleur=ENCRE, taille=10):
        pdf.set_x(x_tot)
        pdf.police("B" if gras else "", taille)
        pdf.set_text_color(*couleur)
        pdf.cell(50, 7, _t(pdf, libelle))
        pdf.cell(36, 7, _t(pdf, nombre(valeur) + " DZD"), align="R")
        pdf.ln(7)

    if remise:
        ligne_total("Sous-total", total_brut)
        ligne_total("Remise", -remise, couleur=GRIS)

    y = pdf.get_y()
    pdf.set_fill_color(*ENCRE)
    pdf.rect(x_tot - 4, y, 90, 12, style="F")
    pdf.set_xy(x_tot, y + 1)
    pdf.police("B", 11.5)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(50, 10, _t(pdf, "TOTAL \u00e0 payer"))
    pdf.cell(36, 10, _t(pdf, nombre(total) + " DZD"), align="R")
    pdf.ln(15)

    if paye > 0:
        ligne_total("D\u00e9j\u00e0 vers\u00e9", paye, couleur=VERT)
        ligne_total("Reste \u00e0 payer", reste, gras=True, couleur=(180, 67, 56) if reste else VERT)

    # ---------------------------------------------------------------- pied
    pdf.ln(4)
    pdf.set_x(marge)
    pdf.police("", 9)
    pdf.set_text_color(*GRIS)
    bas = [MENTIONS.get(doc["type_doc"], "")]
    mode = doc.get("mode_prix") or ""
    if mode == "pose_fourniture":
        bas.append("Prix incluant la fourniture du mat\u00e9riel et la pose.")
    elif mode == "pose":
        bas.append("Prix de pose uniquement \u2014 le mat\u00e9riel est fourni par le client.")
    if doc.get("note"):
        bas.append("Note : " + doc["note"])
    if doc["type_doc"] == "Devis":
        acompte = db.get_param_num("acompte_defaut", 50)
        if acompte:
            bas.append("Acompte demand\u00e9 au d\u00e9marrage : %d %% soit %s DZD."
                       % (int(acompte), nombre(total * acompte / 100)))
        bas.append("Bon pour accord \u2014 date et signature du client :")
    pdf.multi_cell(largeur, 5.5, _t(pdf, "\n".join([b for b in bas if b])))

    if doc["type_doc"] == "Devis":
        y = pdf.get_y() + 4
        pdf.set_draw_color(*TRAIT)
        pdf.rect(marge, y, 80, 22)

    statut = ETAPES_LIB.get(doc.get("statut") or "", "")
    if statut:
        pdf.set_xy(210 - marge - 40, pdf.get_y() + 4)
        pdf.police("B", 8)
        pdf.set_text_color(*BLEU)
        pdf.cell(40, 5, _t(pdf, "Statut : " + statut), align="R")

    if chemin is None:
        chemin = os.path.join(_dossier_sortie(),
                              "%s.pdf" % (doc["numero"] or "document"))
    pdf.output(chemin)
    return chemin
