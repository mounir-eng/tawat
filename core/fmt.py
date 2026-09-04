# -*- coding: utf-8 -*-
"""Formatage : argent, nombres, dates, telephones, liens de messagerie."""
import re
from datetime import date, datetime

DEVISE = "DZD"

MOIS_FR = ["janvier", "f\u00e9vrier", "mars", "avril", "mai", "juin", "juillet",
           "ao\u00fbt", "septembre", "octobre", "novembre", "d\u00e9cembre"]
JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def nombre(v, dec=0):
    try:
        v = float(v or 0)
    except (TypeError, ValueError):
        return "0"
    txt = ("{:,.%df}" % dec).format(v).replace(",", "\u202f").replace(".", ",")
    return txt


def dz(v, suffixe=True, dec=0):
    """125000 -> '125 000 DZD'"""
    return nombre(v, dec) + (" " + DEVISE if suffixe else "")


def dz_court(v):
    """Grands montants abreges pour les tuiles : 1 284 000 -> '1,28 M'"""
    try:
        v = float(v or 0)
    except (TypeError, ValueError):
        v = 0.0
    a = abs(v)
    if a >= 1_000_000:
        return nombre(v / 1_000_000, 2) + " M"
    if a >= 100_000:
        return nombre(v / 1000, 0) + " K"
    return nombre(v, 0)


def pct(v, dec=0):
    return nombre(v, dec) + " %"


def d(valeur):
    """Convertit une valeur quelconque en date (ou None)."""
    if isinstance(valeur, datetime):
        return valeur.date()
    if isinstance(valeur, date):
        return valeur
    if not valeur:
        return None
    for f in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(valeur)[:19], f).date()
        except ValueError:
            continue
    return None


def date_fr(valeur, court=True):
    dd = d(valeur)
    if not dd:
        return "\u2014"
    if court:
        return dd.strftime("%d/%m/%Y")
    return "%d %s %d" % (dd.day, MOIS_FR[dd.month - 1], dd.year)


def mois_libelle(valeur):
    dd = d(valeur)
    if not dd:
        return "Sans date"
    return "%s %d" % (MOIS_FR[dd.month - 1].capitalize(), dd.year)


def mois_cle(valeur):
    dd = d(valeur)
    return dd.strftime("%Y-%m") if dd else "0000-00"


def jours_depuis(valeur):
    dd = d(valeur)
    return (date.today() - dd).days if dd else 0


def initiales(nom):
    mots = [m for m in re.split(r"[\s\-']+", (nom or "?").strip()) if m]
    if not mots:
        return "?"
    if len(mots) == 1:
        return mots[0][:2].upper()
    return (mots[0][0] + mots[1][0]).upper()


def tel_international(tel):
    """'0661 22 33 44' -> '213661223344'"""
    num = re.sub(r"\D", "", tel or "")
    if not num:
        return ""
    if num.startswith("00"):
        num = num[2:]
    if num.startswith("213"):
        return num
    if num.startswith("0"):
        return "213" + num[1:]
    return "213" + num if len(num) == 9 else num


def tel_joli(tel):
    num = re.sub(r"\D", "", tel or "")
    if len(num) == 10 and num.startswith("0"):
        return " ".join([num[0:4], num[4:6], num[6:8], num[8:10]])
    return tel or "\u2014"


def lien_whatsapp(tel, texte=""):
    from urllib.parse import quote
    num = tel_international(tel)
    if not num:
        return ""
    return "https://wa.me/%s?text=%s" % (num, quote(texte))


def lien_viber(tel, texte=""):
    from urllib.parse import quote
    num = tel_international(tel)
    if not num:
        return ""
    return "viber://chat?number=%%2B%s&text=%s" % (num, quote(texte))


def lien_sms(tel, texte=""):
    from urllib.parse import quote
    num = tel_international(tel)
    if not num:
        return ""
    return "sms:+%s?body=%s" % (num, quote(texte))


def arrondi_commercial(montant, pas=500):
    """Arrondit au pas commercial le plus proche (500 DZD par defaut)."""
    try:
        montant = float(montant or 0)
    except (TypeError, ValueError):
        return 0.0
    if pas <= 0:
        return montant
    return round(montant / pas) * pas


def salutation():
    h = datetime.now().hour
    if h < 12:
        return "Sbah el kheir"
    if h < 18:
        return "Bonjour"
    return "Msa el kheir"


def date_du_jour_fr():
    t = date.today()
    return "%s %d %s" % (JOURS_FR[t.weekday()].capitalize(), t.day, MOIS_FR[t.month - 1])
