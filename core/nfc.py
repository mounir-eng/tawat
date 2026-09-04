# -*- coding: utf-8 -*-
"""Base de connaissance m\u00e9tier : types de b\u00e2timent \u2192 pi\u00e8ces \u2192 postes normalis\u00e9s.

Les postes \u00e9lectriques suivent les minima de la norme NF C 15-100 (r\u00e9f\u00e9rence
utilis\u00e9e en Alg\u00e9rie pour l'installation basse tension) : nombre de prises par
pi\u00e8ce, points lumineux, circuits sp\u00e9cialis\u00e9s, protections du tableau.

Chaque poste porte :
  libelle / unite / qte  : la ligne de devis pr\u00e9-remplie
  prix                   : prix indicatif DZD (\u00e9cras\u00e9 par la biblioth\u00e8que si connue)
  norme                  : la r\u00e8gle qui justifie la quantit\u00e9 (affich\u00e9e \u00e0 l'artisan)
  par_m2 / mini          : r\u00e8gle de calcul automatique selon la surface
  obligatoire            : True = minimum r\u00e9glementaire, False = recommand\u00e9/option

Aucune d\u00e9pendance \u00e0 Streamlit : module testable seul.
"""
import math

from . import db


def _p(libelle, unite, qte, prix, norme, par_m2=None, mini=None, obligatoire=True,
       fourn=None):
    """Un poste de devis pre-rempli.

    prix  : prix de POSE par unite (main d'oeuvre + petit materiel de l'artisan)
    fourn : prix de la FOURNITURE par unite (la piece elle-meme), None = bareme
    """
    return {"libelle": libelle, "unite": unite, "qte": qte, "prix": prix, "norme": norme,
            "par_m2": par_m2, "mini": mini, "obligatoire": obligatoire, "fourn": fourn}


# ==========================================================================
#  TYPES DE B\u00c2TIMENT
# ==========================================================================
TYPES_BATIMENT = {
    "appart_neuf": {
        "ar": "\u0634\u0642\u0629 \u062c\u062f\u064a\u062f\u0629", "fr": "Appartement neuf", "icone": "\U0001f3e2",
        "renovation": False,
        "pieces": ["entree", "sejour", "chambre", "cuisine", "sdb", "wc", "couloir",
                   "balcon", "tableau"],
    },
    "appart_reno": {
        "ar": "\u0634\u0642\u0629 \u062a\u062c\u062f\u064a\u062f", "fr": "Appartement r\u00e9novation", "icone": "\U0001f6e0\ufe0f",
        "renovation": True,
        "pieces": ["entree", "sejour", "chambre", "cuisine", "sdb", "wc", "couloir",
                   "balcon", "tableau"],
    },
    "maison_etages": {
        "ar": "\u0645\u0646\u0632\u0644 \u0630\u0648 \u0637\u0648\u0627\u0628\u0642", "fr": "Maison \u00e0 \u00e9tages", "icone": "\U0001f3e1",
        "renovation": False, "etages": True,
        "pieces": ["entree", "sejour", "chambre", "cuisine", "sdb", "wc", "couloir",
                   "escalier", "buanderie", "terrasse", "garage", "tableau"],
    },
    "villa": {
        "ar": "\u0641\u064a\u0644\u0627", "fr": "Villa", "icone": "\U0001f3d8\ufe0f",
        "renovation": False, "etages": True,
        "pieces": ["entree", "sejour", "chambre", "cuisine", "sdb", "wc", "couloir",
                   "escalier", "buanderie", "bureau_dom", "terrasse", "garage",
                   "jardin", "tableau"],
    },
    "bureau": {
        "ar": "\u0645\u0643\u062a\u0628", "fr": "Bureau", "icone": "\U0001f4bc",
        "renovation": False,
        "pieces": ["accueil", "open_space", "bureau_ferme", "salle_reunion", "kitchenette",
                   "sanitaires", "couloir", "local_tech", "tableau"],
    },
    "institution": {
        "ar": "\u0645\u0624\u0633\u0633\u0629", "fr": "Institution / \u00c9tablissement", "icone": "\U0001f3db\ufe0f",
        "renovation": False,
        "pieces": ["accueil", "salle_classe", "bureau_ferme", "salle_reunion", "couloir",
                   "sanitaires", "local_tech", "tableau"],
    },
    "usine": {
        "ar": "\u0645\u0635\u0646\u0639", "fr": "Usine / Atelier", "icone": "\U0001f3ed",
        "renovation": False,
        "pieces": ["hall_prod", "atelier", "reserve", "bureau_ferme", "vestiaire",
                   "sanitaires", "local_tech", "tableau_force"],
    },
    "local": {
        "ar": "\u0645\u062d\u0644 \u062a\u062c\u0627\u0631\u064a", "fr": "Local commercial", "icone": "\U0001f3ea",
        "renovation": False,
        "pieces": ["vitrine", "surface_vente", "reserve", "sanitaires", "tableau"],
    },
}

ORDRE_BATIMENTS = ["appart_neuf", "appart_reno", "maison_etages", "villa",
                   "bureau", "institution", "usine", "local"]


# ==========================================================================
#  NIVEAUX (maison a etages / villa : chaque etage est chiffre separement)
# ==========================================================================
NIVEAUX = {
    "sous_sol": {"ar": "\u0627\u0644\u0642\u0628\u0648 / \u0627\u0644\u0633\u0641\u0644\u064a",
                 "fr": "Sous-sol", "icone": "\u2b07\ufe0f"},
    "rdc": {"ar": "\u0627\u0644\u0637\u0627\u0628\u0642 \u0627\u0644\u0623\u0631\u0636\u064a",
            "fr": "RDC", "icone": "\U0001f3e0"},
    "etage1": {"ar": "\u0627\u0644\u0637\u0627\u0628\u0642 \u0627\u0644\u0623\u0648\u0644",
               "fr": "1er \u00e9tage", "icone": "\u0031\ufe0f\u20e3"},
    "etage2": {"ar": "\u0627\u0644\u0637\u0627\u0628\u0642 \u0627\u0644\u062b\u0627\u0646\u064a",
               "fr": "2e \u00e9tage", "icone": "\u0032\ufe0f\u20e3"},
    "etage3": {"ar": "\u0627\u0644\u0637\u0627\u0628\u0642 \u0627\u0644\u062b\u0627\u0644\u062b",
               "fr": "3e \u00e9tage", "icone": "\u0033\ufe0f\u20e3"},
    "toit": {"ar": "\u0627\u0644\u0633\u0637\u062d", "fr": "Toiture / Terrasse",
             "icone": "\u2600\ufe0f"},
}

ORDRE_NIVEAUX = ["sous_sol", "rdc", "etage1", "etage2", "etage3", "toit"]


def a_des_etages(cle_batiment):
    """Vrai pour les batiments ou l'on chiffre etage par etage."""
    return bool((TYPES_BATIMENT.get(cle_batiment) or {}).get("etages"))


def niveaux_batiment(cle_batiment):
    return list(ORDRE_NIVEAUX) if a_des_etages(cle_batiment) else []


def nom_niveau(cle, langue="ar"):
    info = NIVEAUX.get(cle) or {}
    return info.get(langue) or info.get("fr") or ""


def icone_niveau(cle):
    return (NIVEAUX.get(cle) or {}).get("icone", "")


# ==========================================================================
#  PI\u00c8CES
# ==========================================================================
PIECES = {
    "entree": {"ar": "\u0627\u0644\u0645\u062f\u062e\u0644", "fr": "Entr\u00e9e", "icone": "\U0001f6aa", "surface": 6},
    "sejour": {"ar": "\u063a\u0631\u0641\u0629 \u062c\u0644\u0648\u0633", "fr": "S\u00e9jour / Salon", "icone": "\U0001f6cb\ufe0f", "surface": 24},
    "chambre": {"ar": "\u063a\u0631\u0641\u0629 \u0646\u0648\u0645", "fr": "Chambre", "icone": "\U0001f6cf\ufe0f", "surface": 14},
    "cuisine": {"ar": "\u0627\u0644\u0645\u0637\u0628\u062e", "fr": "Cuisine", "icone": "\U0001f373", "surface": 12},
    "sdb": {"ar": "\u0627\u0644\u062d\u0645\u0627\u0645", "fr": "Salle de bain", "icone": "\U0001f6c1", "surface": 6},
    "wc": {"ar": "\u0627\u0644\u0645\u0631\u062d\u0627\u0636", "fr": "WC", "icone": "\U0001f6bd", "surface": 2},
    "couloir": {"ar": "\u0627\u0644\u0645\u0645\u0631", "fr": "Couloir / D\u00e9gagement", "icone": "\U0001f6b6", "surface": 8},
    "escalier": {"ar": "\u0627\u0644\u0633\u0644\u0627\u0644\u0645", "fr": "Escalier", "icone": "\u2b06\ufe0f", "surface": 6},
    "balcon": {"ar": "\u0627\u0644\u0634\u0631\u0641\u0629", "fr": "Balcon", "icone": "\U0001f33f", "surface": 6},
    "terrasse": {"ar": "\u0627\u0644\u0633\u0637\u062d / \u0627\u0644\u062a\u0631\u0627\u0633", "fr": "Terrasse", "icone": "\u2600\ufe0f", "surface": 20},
    "garage": {"ar": "\u0627\u0644\u0645\u0631\u0622\u0628 / \u0627\u0644\u0642\u0627\u0639\u0629", "fr": "Garage", "icone": "\U0001f697", "surface": 18},
    "buanderie": {"ar": "\u0645\u063a\u0633\u0644\u0629", "fr": "Buanderie", "icone": "\U0001f4a7", "surface": 6},
    "bureau_dom": {"ar": "\u0645\u0643\u062a\u0628 \u0645\u0646\u0632\u0644\u064a", "fr": "Bureau (domicile)", "icone": "\U0001f5a5\ufe0f", "surface": 12},
    "jardin": {"ar": "\u0627\u0644\u062d\u062f\u064a\u0642\u0629 / \u0627\u0644\u062e\u0627\u0631\u062c", "fr": "Jardin / Ext\u00e9rieur", "icone": "\U0001f333", "surface": 40},
    # --- professionnel
    "accueil": {"ar": "\u0627\u0644\u0627\u0633\u062a\u0642\u0628\u0627\u0644", "fr": "Accueil", "icone": "\U0001f6ce\ufe0f", "surface": 20},
    "open_space": {"ar": "\u0642\u0627\u0639\u0629 \u0645\u0641\u062a\u0648\u062d\u0629", "fr": "Open space", "icone": "\U0001f465", "surface": 60},
    "bureau_ferme": {"ar": "\u0645\u0643\u062a\u0628 \u0645\u063a\u0644\u0642", "fr": "Bureau ferm\u00e9", "icone": "\U0001f5a5\ufe0f", "surface": 15},
    "salle_reunion": {"ar": "\u0642\u0627\u0639\u0629 \u0627\u062c\u062a\u0645\u0627\u0639\u0627\u062a", "fr": "Salle de r\u00e9union", "icone": "\U0001f4ca", "surface": 25},
    "salle_classe": {"ar": "\u0642\u0627\u0639\u0629 \u062f\u0631\u0648\u0633", "fr": "Salle de classe", "icone": "\U0001f393", "surface": 45},
    "kitchenette": {"ar": "\u0645\u0637\u0628\u062e \u0635\u063a\u064a\u0631", "fr": "Kitchenette", "icone": "\u2615", "surface": 8},
    "sanitaires": {"ar": "\u0645\u0631\u0627\u0641\u0642 \u0635\u062d\u064a\u0629", "fr": "Sanitaires", "icone": "\U0001f6bb", "surface": 10},
    "vitrine": {"ar": "\u0627\u0644\u0648\u0627\u062c\u0647\u0629 / \u0627\u0644\u0641\u064a\u062a\u0631\u064a\u0646", "fr": "Vitrine", "icone": "\U0001f3ec", "surface": 12},
    "surface_vente": {"ar": "\u0642\u0627\u0639\u0629 \u0627\u0644\u0628\u064a\u0639", "fr": "Surface de vente", "icone": "\U0001f6d2", "surface": 50},
    "reserve": {"ar": "\u0627\u0644\u0645\u062e\u0632\u0646", "fr": "R\u00e9serve / Stock", "icone": "\U0001f4e6", "surface": 20},
    "hall_prod": {"ar": "\u0642\u0627\u0639\u0629 \u0627\u0644\u0625\u0646\u062a\u0627\u062c", "fr": "Hall de production", "icone": "\U0001f3ed", "surface": 200},
    "atelier": {"ar": "\u0648\u0631\u0634\u0629", "fr": "Atelier", "icone": "\U0001f527", "surface": 60},
    "vestiaire": {"ar": "\u063a\u0631\u0641\u0629 \u062a\u063a\u064a\u064a\u0631", "fr": "Vestiaire", "icone": "\U0001f455", "surface": 15},
    "local_tech": {"ar": "\u0627\u0644\u063a\u0631\u0641\u0629 \u0627\u0644\u062a\u0642\u0646\u064a\u0629", "fr": "Local technique", "icone": "\u2699\ufe0f", "surface": 8},
    # --- transverse
    "tableau": {"ar": "\u0627\u0644\u0644\u0648\u062d\u0629 \u0627\u0644\u0643\u0647\u0631\u0628\u0627\u0626\u064a\u0629 \u0648\u0627\u0644\u0623\u0631\u0636\u064a",
                "fr": "Tableau \u00e9lectrique & terre", "icone": "\U0001f50c", "surface": 0},
    "tableau_force": {"ar": "\u0644\u0648\u062d\u0629 \u0627\u0644\u0642\u0648\u0629 (\u062b\u0644\u0627\u062b\u064a \u0627\u0644\u0623\u0637\u0648\u0627\u0631)",
                      "fr": "Tableau force (triphas\u00e9)", "icone": "\u26a1", "surface": 0},
}


# ==========================================================================
#  POSTES \u00c9LECTRIQUES \u2014 NF C 15-100
# ==========================================================================
ELEC = {
    "entree": [
        _p("Point lumineux complet", "U", 1, 3200,
           "NF C 15-100 : au moins 1 point d'\u00e9clairage par entr\u00e9e, command\u00e9 \u00e0 la porte."),
        _p("Interrupteur va-et-vient", "U", 2, 1000,
           "Commande de l'entr\u00e9e depuis la porte et depuis le couloir (va-et-vient)."),
        _p("Prise de courant", "U", 1, 800,
           "1 prise 16A minimum dans l'entr\u00e9e."),
        _p("Bouton-poussoir sonnette", "U", 1, 800,
           "Sonnette ext\u00e9rieure : recommand\u00e9e.", obligatoire=False),
        _p("Vid\u00e9ophone / Interphone", "U", 1, 5000,
           "Contr\u00f6le d'acc\u00e8s : option tr\u00e8s demand\u00e9e.", obligatoire=False),
    ],
    "sejour": [
        _p("Prise de courant", "U", 6, 800,
           "NF C 15-100 : 1 prise 16A par tranche de 4 m\u00b2, avec un minimum de 5 au s\u00e9jour.",
           par_m2=4, mini=5),
        _p("Point lumineux complet", "U", 1, 3200,
           "Au moins 1 point d'\u00e9clairage au plafond (DCL) par pi\u00e8ce."),
        _p("Interrupteur va-et-vient", "U", 2, 1000,
           "Commande de l'\u00e9clairage \u00e0 2 endroits (entr\u00e9e du salon + fond de pi\u00e8ce)."),
        _p("Prise TV / Coaxiale", "U", 1, 1500,
           "NF C 15-100 : 1 prise TV minimum au s\u00e9jour, plac\u00e9e \u00e0 c\u00f4t\u00e9 de 2 prises 16A."),
        _p("Prise r\u00e9seau RJ45", "U", 1, 1500,
           "NF C 15-100 : au moins 1 prise RJ45 au s\u00e9jour (2 si logement > 100 m\u00b2)."),
        _p("Prise pour climatiseur", "U", 1, 1300,
           "Circuit d\u00e9di\u00e9 conseill\u00e9 pour la climatisation du salon.", obligatoire=False),
        _p("Bo\u00eete de d\u00e9rivation", "U", 2, 800,
           "Bo\u00eetes de d\u00e9rivation accessibles pour le tirage des c\u00e2bles.", obligatoire=False),
    ],
    "chambre": [
        _p("Prise de courant", "U", 3, 800,
           "NF C 15-100 : 3 prises 16A minimum par chambre.", par_m2=6, mini=3),
        _p("Point lumineux complet", "U", 1, 3200,
           "1 point d'\u00e9clairage au plafond (DCL) command\u00e9 \u00e0 l'entr\u00e9e de la chambre."),
        _p("Interrupteur simple", "U", 1, 800,
           "Commande de l'\u00e9clairage \u00e0 la porte."),
        _p("Interrupteur va-et-vient", "U", 2, 1000,
           "Confort : commande porte + t\u00eate de lit.", obligatoire=False),
        _p("Prise r\u00e9seau RJ45", "U", 1, 1500,
           "NF C 15-100 : 1 prise RJ45 par chambre."),
        _p("Prise TV / Coaxiale", "U", 1, 1500,
           "Prise TV en chambre : recommand\u00e9e.", obligatoire=False),
        _p("Prise pour climatiseur", "U", 1, 1300,
           "Circuit d\u00e9di\u00e9 pour split : recommand\u00e9.", obligatoire=False),
    ],
    "cuisine": [
        _p("Prise de courant", "U", 6, 800,
           "NF C 15-100 : 6 prises 16A minimum en cuisine, dont 4 au-dessus du plan de travail.",
           mini=6),
        _p("Prise avec mise \u00e0 la terre", "U", 3, 900,
           "3 circuits sp\u00e9cialis\u00e9s obligatoires : lave-linge, lave-vaisselle, four."),
        _p("Prise triphas\u00e9e 380V", "U", 1, 2000,
           "Plaque de cuisson : circuit d\u00e9di\u00e9 32A (ou triphas\u00e9 selon l'appareil)."),
        _p("Point lumineux complet", "U", 2, 3200,
           "\u00c9clairage g\u00e9n\u00e9ral + \u00e9clairage du plan de travail."),
        _p("Interrupteur simple", "U", 2, 800,
           "Commande s\u00e9par\u00e9e : plafond et plan de travail."),
        _p("Prise pour chauffe-eau / r\u00e9sistance", "U", 1, 1300,
           "Chauffe-eau \u00e9lectrique : circuit d\u00e9di\u00e9 avec protection propre.", obligatoire=False),
        _p("Prise de courant", "U", 1, 800,
           "Prise hotte aspirante.", obligatoire=False),
    ],
    "sdb": [
        _p("Prise avec mise \u00e0 la terre", "U", 1, 900,
           "NF C 15-100 : prise 16A autoris\u00e9e hors volume 2, \u00e0 60 cm minimum du point d'eau."),
        _p("Point lumineux complet", "U", 1, 3200,
           "\u00c9clairage IP44 minimum ; luminaire classe II en volume 2."),
        _p("Interrupteur simple", "U", 1, 800,
           "Interrupteur plac\u00e9 hors volumes 0/1/2 (ou \u00e0 l'ext\u00e9rieur de la pi\u00e8ce)."),
        _p("Mise \u00e0 la terre", "Forfait", 1, 9000,
           "Liaison \u00e9quipotentielle locale (LEL) OBLIGATOIRE : baignoire, douche, canalisations."),
        _p("Prise pour chauffe-eau / r\u00e9sistance", "U", 1, 1300,
           "Chauffe-eau : circuit d\u00e9di\u00e9 prot\u00e9g\u00e9, hors volumes.", obligatoire=False),
        _p("Point lumineux complet", "U", 1, 3200,
           "\u00c9clairage miroir / applique : recommand\u00e9.", obligatoire=False),
    ],
    "wc": [
        _p("Point lumineux complet", "U", 1, 3200,
           "1 point d'\u00e9clairage obligatoire."),
        _p("Interrupteur simple", "U", 1, 800, "Commande \u00e0 la porte."),
        _p("Prise de courant", "U", 1, 800,
           "Prise recommand\u00e9e (ventilation, hygi\u00e8ne).", obligatoire=False),
    ],
    "couloir": [
        _p("Point lumineux complet", "U", 1, 3200,
           "NF C 15-100 : 1 point d'\u00e9clairage par d\u00e9gagement.", par_m2=10, mini=1),
        _p("Interrupteur va-et-vient", "U", 2, 1000,
           "Allumage/extinction aux deux extr\u00e9mit\u00e9s du couloir."),
        _p("Prise de courant", "U", 1, 800,
           "NF C 15-100 : 1 prise 16A si le d\u00e9gagement d\u00e9passe 4 m\u00b2."),
    ],
    "escalier": [
        _p("Point lumineux complet", "U", 2, 3200,
           "\u00c9clairage de chaque vol\u00e9e d'escalier (s\u00e9curit\u00e9 de circulation).", par_m2=8, mini=2),
        _p("Bouton-poussoir t\u00e9l\u00e9rupteur", "U", 3, 800,
           "Commande par t\u00e9l\u00e9rupteur \u00e0 chaque niveau (haut, bas, palier)."),
        _p("Prise de courant", "U", 1, 800, "Prise de palier : entretien.", obligatoire=False),
    ],
    "balcon": [
        _p("Point lumineux complet", "U", 1, 3200,
           "Luminaire \u00e9tanche IP44 minimum en ext\u00e9rieur prot\u00e9g\u00e9."),
        _p("Interrupteur simple", "U", 1, 800, "Commande depuis l'int\u00e9rieur."),
        _p("Prise avec mise \u00e0 la terre", "U", 1, 900,
           "Prise \u00e9tanche IP44 avec terre : recommand\u00e9e.", obligatoire=False),
    ],
    "terrasse": [
        _p("Point lumineux complet", "U", 2, 3200,
           "\u00c9clairage ext\u00e9rieur IP44/IP65 selon exposition.", par_m2=15, mini=1),
        _p("Prise avec mise \u00e0 la terre", "U", 1, 900,
           "Prise ext\u00e9rieure \u00e9tanche prot\u00e9g\u00e9e par diff\u00e9rentiel 30 mA."),
        _p("Interrupteur va-et-vient", "U", 2, 1000,
           "Commande int\u00e9rieur/ext\u00e9rieur.", obligatoire=False),
    ],
    "garage": [
        _p("Point lumineux complet", "U", 2, 3200,
           "\u00c9clairage suffisant (1 point / 15 m\u00b2), luminaire \u00e9tanche conseill\u00e9.",
           par_m2=15, mini=1),
        _p("Prise avec mise \u00e0 la terre", "U", 2, 900,
           "NF C 15-100 : prises avec terre ; circuit d\u00e9di\u00e9 si atelier.", mini=1),
        _p("Interrupteur simple", "U", 1, 800, "Commande \u00e0 l'entr\u00e9e du garage."),
        _p("Prise triphas\u00e9e 380V", "U", 1, 2000,
           "Alimentation portail automatique / machine d'atelier.", obligatoire=False),
    ],
    "buanderie": [
        _p("Prise avec mise \u00e0 la terre", "U", 3, 900,
           "Circuits sp\u00e9cialis\u00e9s : lave-linge, s\u00e8che-linge, cong\u00e9lateur."),
        _p("Point lumineux complet", "U", 1, 3200, "1 point d'\u00e9clairage."),
        _p("Interrupteur simple", "U", 1, 800, "Commande \u00e0 la porte."),
    ],
    "bureau_dom": [
        _p("Prise de courant", "U", 4, 800,
           "Poste de travail : 4 prises 16A minimum (1 / 4 m\u00b2).", par_m2=4, mini=4),
        _p("Prise r\u00e9seau RJ45", "U", 2, 1500,
           "2 prises RJ45 par poste de travail (PC + imprimante/box)."),
        _p("Point lumineux complet", "U", 1, 3200, "\u00c9clairage g\u00e9n\u00e9ral du bureau."),
        _p("Interrupteur simple", "U", 1, 800, "Commande \u00e0 la porte."),
    ],
    "jardin": [
        _p("Point lumineux complet", "U", 4, 3200,
           "\u00c9clairage ext\u00e9rieur IP65, circuit prot\u00e9g\u00e9 par diff\u00e9rentiel 30 mA.",
           par_m2=25, mini=2),
        _p("Prise avec mise \u00e0 la terre", "U", 2, 900,
           "Prises ext\u00e9rieures \u00e9tanches IP44 minimum.", mini=1),
        _p("Bouton-poussoir t\u00e9l\u00e9rupteur", "U", 2, 800,
           "Commande d\u00e9port\u00e9e de l'\u00e9clairage ext\u00e9rieur.", obligatoire=False),
        _p("Mise \u00e0 la terre", "Forfait", 1, 9000,
           "Piquet de terre + liaison : indispensable pour l'ext\u00e9rieur.", obligatoire=False),
    ],
    # ------------------------------------------------ professionnel
    "accueil": [
        _p("Point lumineux complet", "U", 4, 3200,
           "\u00c9clairage 300 lux minimum en zone d'accueil (1 point / 6 m\u00b2).",
           par_m2=6, mini=2),
        _p("Prise de courant", "U", 4, 800, "Prises banque d'accueil + attente.",
           par_m2=6, mini=4),
        _p("Prise r\u00e9seau RJ45", "U", 2, 1500, "Poste d'accueil : t\u00e9l\u00e9phone + PC."),
        _p("Vid\u00e9ophone / Interphone", "U", 1, 5000, "Contr\u00f4le d'acc\u00e8s visiteurs.",
           obligatoire=False),
        _p("Interrupteur va-et-vient", "U", 2, 1000, "Commande double de l'\u00e9clairage."),
    ],
    "open_space": [
        _p("Prise de courant", "U", 12, 800,
           "4 prises 16A par poste de travail (norme bureautique : 1 poste / 10 m\u00b2).",
           par_m2=3, mini=8),
        _p("Prise r\u00e9seau RJ45", "U", 6, 1500,
           "2 prises RJ45 par poste de travail, cheminement en goulotte.",
           par_m2=10, mini=4),
        _p("Point lumineux complet", "U", 8, 3200,
           "\u00c9clairage 400-500 lux pour travail sur \u00e9cran (1 point / 8 m\u00b2).",
           par_m2=8, mini=4),
        _p("Interrupteur double", "U", 2, 1000, "Commande par zone d'\u00e9clairage."),
        _p("Tableau de protection 10 modules", "U", 1, 5000,
           "Tableau divisionnaire de zone avec diff\u00e9rentiel 30 mA d\u00e9di\u00e9."),
    ],
    "bureau_ferme": [
        _p("Prise de courant", "U", 4, 800, "4 prises 16A par poste de travail.",
           par_m2=4, mini=4),
        _p("Prise r\u00e9seau RJ45", "U", 2, 1500, "2 prises RJ45 par poste."),
        _p("Point lumineux complet", "U", 2, 3200, "\u00c9clairage 400 lux au plan de travail.",
           par_m2=8, mini=1),
        _p("Interrupteur simple", "U", 1, 800, "Commande \u00e0 la porte."),
        _p("Prise t\u00e9l\u00e9phone (RJ11)", "U", 1, 1000, "Ligne t\u00e9l\u00e9phonique d\u00e9di\u00e9e.",
           obligatoire=False),
    ],
    "salle_reunion": [
        _p("Prise de courant", "U", 6, 800, "Prises table de r\u00e9union + p\u00e9riph\u00e9rie.",
           par_m2=5, mini=4),
        _p("Prise r\u00e9seau RJ45", "U", 2, 1500, "Visioconf\u00e9rence + \u00e9cran connect\u00e9."),
        _p("Point lumineux complet", "U", 4, 3200, "\u00c9clairage variable (1 point / 7 m\u00b2).",
           par_m2=7, mini=2),
        _p("Interrupteur double", "U", 1, 1000, "Commande 2 zones (projection / g\u00e9n\u00e9ral)."),
        _p("Prise TV / Coaxiale", "U", 1, 1500, "\u00c9cran de pr\u00e9sentation.", obligatoire=False),
    ],
    "salle_classe": [
        _p("Point lumineux complet", "U", 6, 3200,
           "\u00c9clairage 300-500 lux uniforme (1 point / 8 m\u00b2), obligatoire en ERP.",
           par_m2=8, mini=4),
        _p("Prise de courant", "U", 6, 800,
           "Prises p\u00e9dagogiques + estrade, hors de port\u00e9e directe des \u00e9l\u00e8ves.",
           par_m2=10, mini=4),
        _p("Prise r\u00e9seau RJ45", "U", 2, 1500, "Poste enseignant + \u00e9quipement num\u00e9rique."),
        _p("Interrupteur double", "U", 2, 1000, "Commande par rang\u00e9e (\u00e9conomie d'\u00e9nergie)."),
        _p("Point lumineux complet", "U", 2, 3200,
           "Blocs autonomes d'\u00e9clairage de s\u00e9curit\u00e9 (BAES) : obligatoire en ERP."),
    ],
    "kitchenette": [
        _p("Prise avec mise \u00e0 la terre", "U", 4, 900,
           "Prises plan de travail + machine \u00e0 caf\u00e9 / micro-ondes (circuits s\u00e9par\u00e9s).",
           mini=3),
        _p("Point lumineux complet", "U", 1, 3200, "\u00c9clairage du coin cuisine."),
        _p("Interrupteur simple", "U", 1, 800, "Commande \u00e0 l'entr\u00e9e."),
        _p("Prise pour chauffe-eau / r\u00e9sistance", "U", 1, 1300, "Chauffe-eau d'appoint.",
           obligatoire=False),
    ],
    "sanitaires": [
        _p("Point lumineux complet", "U", 2, 3200, "\u00c9clairage IP44 par cabine / zone lavabo.",
           par_m2=6, mini=1),
        _p("Interrupteur simple", "U", 1, 800, "Commande hors volumes humides."),
        _p("Prise avec mise \u00e0 la terre", "U", 1, 900,
           "Prise s\u00e8che-mains / lavabo, hors volume 2, prot\u00e9g\u00e9e 30 mA."),
        _p("Mise \u00e0 la terre", "Forfait", 1, 9000,
           "Liaison \u00e9quipotentielle des canalisations : obligatoire."),
    ],
    "vitrine": [
        _p("Point lumineux complet", "U", 4, 3200,
           "\u00c9clairage vitrine sur circuit s\u00e9par\u00e9 et commandable ind\u00e9pendamment.",
           par_m2=3, mini=2),
        _p("Prise de courant", "U", 2, 800, "Prises enseigne / animation vitrine."),
        _p("Interrupteur double", "U", 1, 1000, "Commande vitrine / enseigne s\u00e9par\u00e9e."),
        _p("Bo\u00eete de d\u00e9rivation", "U", 2, 800, "Raccordements en faux plafond de vitrine.",
           obligatoire=False),
    ],
    "surface_vente": [
        _p("Point lumineux complet", "U", 8, 3200,
           "\u00c9clairage commercial 500 lux (1 point / 7 m\u00b2).", par_m2=7, mini=4),
        _p("Prise de courant", "U", 6, 800, "Caisse, TPE, mobilier, entretien.",
           par_m2=10, mini=4),
        _p("Prise r\u00e9seau RJ45", "U", 2, 1500, "Caisse enregistreuse + TPE en r\u00e9seau."),
        _p("Point lumineux complet", "U", 2, 3200,
           "BAES \u2014 \u00e9clairage de s\u00e9curit\u00e9 et signal\u00e9tique de sortie : obligatoire (ERP)."),
        _p("Tableau de protection 10 modules", "U", 1, 5000,
           "Tableau du local avec diff\u00e9rentiels 30 mA et coupure d'urgence accessible."),
    ],
    "reserve": [
        _p("Point lumineux complet", "U", 2, 3200, "\u00c9clairage 150 lux minimum (1 point / 12 m\u00b2).",
           par_m2=12, mini=1),
        _p("Prise avec mise \u00e0 la terre", "U", 2, 900, "Prises de service avec terre.", mini=1),
        _p("Interrupteur simple", "U", 1, 800, "Commande \u00e0 l'entr\u00e9e du stock."),
    ],
    "hall_prod": [
        _p("Prise triphas\u00e9e 380V", "U", 6, 2000,
           "Alimentation des machines en triphas\u00e9 380V (prises P17 verrouillables).",
           par_m2=40, mini=3),
        _p("Point lumineux complet", "U", 10, 3200,
           "\u00c9clairage industriel haute baie LED, 300-500 lux selon poste (1 / 20 m\u00b2).",
           par_m2=20, mini=6),
        _p("Prise avec mise \u00e0 la terre", "U", 6, 900,
           "Prises 16A de service r\u00e9parties, prot\u00e9g\u00e9es 30 mA.", par_m2=40, mini=4),
        _p("Mise \u00e0 la terre", "Forfait", 1, 9000,
           "Mise \u00e0 la terre renforc\u00e9e des masses et des machines : obligatoire."),
        _p("Point lumineux complet", "U", 4, 3200,
           "\u00c9clairage de s\u00e9curit\u00e9 et d'\u00e9vacuation (BAES) : obligatoire."),
        _p("Bo\u00eete de d\u00e9rivation", "U", 6, 800,
           "Chemins de c\u00e2bles et bo\u00eetes \u00e9tanches IP55 en zone de production.",
           obligatoire=False),
    ],
    "atelier": [
        _p("Prise triphas\u00e9e 380V", "U", 3, 2000, "Machines d'atelier en triphas\u00e9.",
           par_m2=25, mini=2),
        _p("Prise avec mise \u00e0 la terre", "U", 4, 900, "Prises 16A avec terre, coffret \u00e9tanche.",
           par_m2=15, mini=3),
        _p("Point lumineux complet", "U", 4, 3200, "\u00c9clairage 500 lux au poste de travail.",
           par_m2=15, mini=2),
        _p("Tableau de protection 10 modules", "U", 1, 5000,
           "Coffret d'atelier : disjoncteurs par machine + arr\u00eat d'urgence."),
    ],
    "vestiaire": [
        _p("Point lumineux complet", "U", 2, 3200, "\u00c9clairage 200 lux, IP44 si douches.",
           par_m2=10, mini=1),
        _p("Prise avec mise \u00e0 la terre", "U", 1, 900, "Prise de service prot\u00e9g\u00e9e 30 mA."),
        _p("Interrupteur simple", "U", 1, 800, "Commande \u00e0 l'entr\u00e9e."),
    ],
    "local_tech": [
        _p("Point lumineux complet", "U", 1, 3200, "\u00c9clairage du local technique."),
        _p("Prise avec mise \u00e0 la terre", "U", 2, 900,
           "Prises de maintenance pr\u00e8s des \u00e9quipements."),
        _p("Mise \u00e0 la terre", "Forfait", 1, 9000,
           "Barrette de terre principale et liaisons \u00e9quipotentielles."),
    ],
    "tableau": [
        _p("Tableau de protection 10 modules", "U", 1, 5000,
           "NF C 15-100 : tableau avec 20 % de modules libres pour \u00e9volution."),
        _p("Mise \u00e0 la terre", "Forfait", 1, 9000,
           "Prise de terre + piquet + liaison \u00e9quipotentielle : OBLIGATOIRE."),
        _p("Sonnette / Cloche", "U", 1, 1500, "Sonnette d'entr\u00e9e raccord\u00e9e au tableau.",
           obligatoire=False),
        _p("Bo\u00eete de d\u00e9rivation", "U", 4, 800,
           "GTL / goulotte technique : cheminement des d\u00e9parts.", obligatoire=False),
    ],
    "tableau_force": [
        _p("Tableau de protection 10 modules", "U", 2, 5000,
           "Tableau g\u00e9n\u00e9ral basse tension (TGBT) + tableaux divisionnaires."),
        _p("Prise triphas\u00e9e 380V", "U", 2, 2000, "D\u00e9parts de force triphas\u00e9s prot\u00e9g\u00e9s."),
        _p("Mise \u00e0 la terre", "Forfait", 1, 9000,
           "R\u00e9seau de terre industriel, contr\u00f4le de continuit\u00e9 : obligatoire."),
    ],
}

# Postes suppl\u00e9mentaires en r\u00e9novation (ajout\u00e9s \u00e0 chaque pi\u00e8ce choisie)
CABLAGE = [
    _p("C\u00e2ble 3G1,5 mm\u00b2 (\u00e9clairage)", "ml", 20, 220,
       "NF C 15-100 : section 1,5 mm\u00b2 pour les circuits d'\u00e9clairage (protection 10 A).",
       par_m2=0.8, mini=15, fourn=180),
    _p("C\u00e2ble 3G2,5 mm\u00b2 (prises)", "ml", 25, 300,
       "NF C 15-100 : section 2,5 mm\u00b2 pour les circuits de prises 16 A (protection 20 A).",
       par_m2=0.6, mini=20, fourn=260),
    _p("Gaine ICTA \u00d820 encastr\u00e9e", "ml", 30, 150,
       "Gaine annel\u00e9e ICTA encastr\u00e9e ou en faux plafond : 1 circuit par gaine.",
       par_m2=0.5, mini=20, fourn=90),
    _p("Tirage et raccordement des c\u00e2bles", "U", 8, 350,
       "Main-d'oeuvre de tirage : 1 forfait par point (prise, commande, luminaire).",
       par_m2=3, mini=5, fourn=0),
]

# C\u00e2blage du tableau et de l'arriv\u00e9e (pas de surface : quantit\u00e9s forfaitaires)
CABLAGE_TABLEAU = [
    _p("C\u00e2ble 3G6 mm\u00b2 (circuits sp\u00e9cialis\u00e9s)", "ml", 15, 620,
       "Section 6 mm\u00b2 pour les circuits de forte puissance : chauffe-eau, plaque de cuisson.",
       mini=10, fourn=550),
    _p("C\u00e2ble 3G10 mm\u00b2 (arriv\u00e9e / colonne montante)", "ml", 10, 950,
       "Liaison au disjoncteur de branchement (AGCP) : 10 mm\u00b2 minimum.",
       mini=6, fourn=850),
    _p("Conducteur de terre 16 mm\u00b2 vert-jaune", "ml", 12, 400,
       "NF C 15-100 : conducteur principal de protection jusqu'\u00e0 la barrette de terre.",
       mini=8, fourn=350),
    _p("Goulotte GTL 250 mm", "ml", 3, 1800,
       "Gaine technique de logement (GTL) : regroupe arriv\u00e9e, tableau et communication.",
       mini=2, fourn=1600),
]

# Prix indicatif de la FOURNITURE par unite (la piece seule, hors pose).
# Utilise uniquement en mode "Pose et fourniture". La bibliotheque de prix de
# l'artisan (colonne cout_materiaux) est toujours prioritaire.
FOURNITURE = {
    "Interrupteur simple": 550,
    "Interrupteur double": 850,
    "Interrupteur va-et-vient": 700,
    "Prise de courant": 500,
    "Prise avec mise \u00e0 la terre": 650,
    "Prise triphas\u00e9e 380V": 2400,
    "Prise pour climatiseur": 900,
    "Prise TV / Coaxiale": 650,
    "Prise pour chauffe-eau / r\u00e9sistance": 900,
    "Prise r\u00e9seau RJ45": 900,
    "Prise t\u00e9l\u00e9phone (RJ11)": 550,
    "Bouton-poussoir t\u00e9l\u00e9rupteur": 700,
    "Bouton-poussoir sonnette": 550,
    "Sonnette / Cloche": 1600,
    "Bo\u00eete de d\u00e9rivation": 200,
    "Vid\u00e9ophone / Interphone": 11000,
    "Tableau de protection 6 modules": 6500,
    "Tableau de protection 10 modules": 11500,
    "Point lumineux complet": 1400,
    "Mise \u00e0 la terre": 4500,
    "Saign\u00e9es et rebouchage": 60,
    "D\u00e9pose ancienne installation": 0,
    "Protection sols et mobilier": 1200,
    "Enduit de lissage 2 passes": 120,
    "Peinture int\u00e9rieure 2 couches": 220,
    "Peinture plafond 2 couches": 240,
    "Alimentation eau PPR par point": 1800,
    "\u00c9vacuation PVC par point": 1400,
    "Pose sanitaire (WC / lavabo)": 9000,
    "Mise en eau et essais": 0,
    "Pose carrelage sol 40x40": 900,
    "Plinthes et joints": 180,
    "Faux plafond placo simple": 1100,
    "Corniche pl\u00e2tre pos\u00e9e": 350,
    "Mur en parpaing 20 cm pos\u00e9": 900,
    "Enduit ciment int\u00e9rieur": 250,
}

ELEC_RENOVATION = [
    _p("Saign\u00e9es et rebouchage", "ml", 10, 700,
       "R\u00e9novation : saign\u00e9es pour encastrement des gaines, puis rebouchage.",
       par_m2=2, mini=5),
    _p("D\u00e9pose ancienne installation", "Forfait", 1, 4000,
       "R\u00e9novation : retrait de l'ancien appareillage et des c\u00e2bles hors normes."),
]


# ==========================================================================
#  AUTRES M\u00c9TIERS (m\u00eame parcours pi\u00e8ce par pi\u00e8ce)
# ==========================================================================
def _peinture(surface_murs=2.6):
    return [
        _p("Protection sols et mobilier", "Forfait", 1, 4000, "Pr\u00e9paration avant travaux."),
        _p("Enduit de lissage 2 passes", "m2", 40, 350, "Surface murs \u2248 p\u00e9rim\u00e8tre \u00d7 hauteur.",
           par_m2=0.4),
        _p("Peinture int\u00e9rieure 2 couches", "m2", 40, 550, "2 couches sur murs pr\u00e9par\u00e9s.",
           par_m2=0.4),
        _p("Peinture plafond 2 couches", "m2", 14, 600, "Plafond = surface au sol.", par_m2=1),
    ]


AUTRES = {
    "Peinture": {cle: _peinture() for cle in
                 ["entree", "sejour", "chambre", "cuisine", "couloir", "escalier", "bureau_dom",
                  "accueil", "open_space", "bureau_ferme", "salle_reunion", "salle_classe",
                  "surface_vente", "reserve", "vestiaire", "buanderie", "garage"]},
    "Plomberie": {
        "cuisine": [
            _p("Alimentation eau PPR par point", "U", 2, 4500, "\u00c9vier + lave-vaisselle."),
            _p("\u00c9vacuation PVC par point", "U", 2, 3500, "\u00c9vier + machine."),
            _p("Mise en eau et essais", "Forfait", 1, 5000, "Essais d'\u00e9tanch\u00e9it\u00e9."),
        ],
        "sdb": [
            _p("Alimentation eau PPR par point", "U", 4, 4500, "Douche, lavabo, WC, chauffe-eau."),
            _p("\u00c9vacuation PVC par point", "U", 3, 3500, "Douche, lavabo, WC."),
            _p("Pose sanitaire (WC / lavabo)", "U", 3, 6000, "Pose des appareils sanitaires."),
            _p("Mise en eau et essais", "Forfait", 1, 5000, "Essais et mise en service."),
        ],
        "wc": [
            _p("Alimentation eau PPR par point", "U", 1, 4500, "Alimentation WC."),
            _p("\u00c9vacuation PVC par point", "U", 1, 3500, "\u00c9vacuation WC."),
            _p("Pose sanitaire (WC / lavabo)", "U", 1, 6000, "Pose WC."),
        ],
        "buanderie": [
            _p("Alimentation eau PPR par point", "U", 2, 4500, "Machines \u00e0 laver."),
            _p("\u00c9vacuation PVC par point", "U", 2, 3500, "\u00c9vacuations machines."),
        ],
        "sanitaires": [
            _p("Alimentation eau PPR par point", "U", 4, 4500, "Lavabos et WC collectifs.",
               par_m2=3, mini=2),
            _p("\u00c9vacuation PVC par point", "U", 4, 3500, "\u00c9vacuations collectives.",
               par_m2=3, mini=2),
            _p("Pose sanitaire (WC / lavabo)", "U", 4, 6000, "Appareils sanitaires.",
               par_m2=3, mini=2),
        ],
        "kitchenette": [
            _p("Alimentation eau PPR par point", "U", 1, 4500, "\u00c9vier."),
            _p("\u00c9vacuation PVC par point", "U", 1, 3500, "\u00c9vacuation \u00e9vier."),
        ],
    },
    "Carrelage": {cle: [
        _p("Pose carrelage sol 40x40", "m2", 14, 1200, "Surface au sol de la pi\u00e8ce.", par_m2=1),
        _p("Plinthes et joints", "ml", 15, 400, "P\u00e9rim\u00e8tre de la pi\u00e8ce.", par_m2=1.1),
    ] for cle in ["entree", "sejour", "chambre", "cuisine", "couloir", "garage", "buanderie",
                  "accueil", "open_space", "bureau_ferme", "surface_vente", "reserve",
                  "terrasse", "balcon"]},
    "Pl\u00e2tre / Placo": {cle: [
        _p("Faux plafond placo simple", "m2", 14, 2200, "Surface de plafond \u00e0 traiter.", par_m2=1),
        _p("Corniche pl\u00e2tre pos\u00e9e", "ml", 15, 900, "P\u00e9rim\u00e8tre du plafond.", par_m2=1.1),
    ] for cle in ["entree", "sejour", "chambre", "couloir", "accueil", "open_space",
                  "bureau_ferme", "salle_reunion", "salle_classe", "surface_vente"]},
    "Ma\u00e7onnerie": {cle: [
        _p("Mur en parpaing 20 cm pos\u00e9", "m2", 10, 2600, "Cloisons \u00e0 monter."),
        _p("Enduit ciment int\u00e9rieur", "m2", 20, 900, "Enduit des surfaces mont\u00e9es."),
    ] for cle in ["sejour", "chambre", "cuisine", "garage", "reserve", "atelier", "hall_prod"]},
}


# ==========================================================================
#  API
# ==========================================================================
def metiers_actifs():
    """M\u00e9tiers dont on propose les postes, d'apr\u00e8s le choix fait \u00e0 l'inscription.

    \u00c9lectricien -> ['\u00c9lectricit\u00e9'] uniquement : aucune suggestion d'un autre corps
    de m\u00e9tier. Entrepreneur / Multi-services -> tous les m\u00e9tiers.
    """
    from . import catalog
    metiers = catalog.metiers_artisan()
    if not metiers:
        return ["\u00c9lectricit\u00e9"] + [m for m in AUTRES if m != "\u00c9lectricit\u00e9"]
    resultat = []
    for m in metiers:
        if m in ("\u00c9lectricit\u00e9",):
            resultat.append("\u00c9lectricit\u00e9")
        elif m in AUTRES:
            resultat.append(m)
        elif m == "Salle de bain compl\u00e8te":
            resultat.append("Plomberie")
        elif m == "\u00c9tanch\u00e9it\u00e9 terrasse":
            resultat.append("Ma\u00e7onnerie")
    return resultat or ["\u00c9lectricit\u00e9"]


def postes_metier(metier, piece):
    if metier == "\u00c9lectricit\u00e9":
        return ELEC.get(piece, [])
    return AUTRES.get(metier, {}).get(piece, [])


def pieces_batiment(cle_batiment):
    """Pi\u00e8ces propos\u00e9es pour ce b\u00e2timent, limit\u00e9es \u00e0 celles o\u00f9 le m\u00e9tier a des postes."""
    bat = TYPES_BATIMENT.get(cle_batiment) or {}
    metiers = metiers_actifs()
    retenues = []
    for piece in bat.get("pieces", []):
        if any(postes_metier(m, piece) for m in metiers):
            retenues.append(piece)
    return retenues


def quantite_norme(poste, surface=0.0):
    """Quantit\u00e9 conseill\u00e9e : applique la r\u00e8gle par m\u00b2 puis le minimum de la norme."""
    qte = float(poste.get("qte") or 1)
    par_m2 = poste.get("par_m2")
    if par_m2 and surface and float(surface) > 0:
        # par_m2 = "1 unite par tranche de X m2" (ex : 1 prise / 4 m2 au sejour).
        # Pour les metrages (peinture, plinthes) X est fractionnaire : 0.4 => 2,5 m2/m2.
        qte = math.ceil(float(surface) / float(par_m2))
    mini = poste.get("mini")
    if mini:
        qte = max(qte, float(mini))
    return float(max(1.0, qte))


def prix_pratique(libelle, unite, defaut=0.0):
    """Prix de la biblioth\u00e8que (prix r\u00e9ellement pratiqu\u00e9) sinon prix indicatif."""
    row = db.one("SELECT prix_unitaire, cout_materiaux, cout_pose FROM catalogue "
                 "WHERE libelle=? AND unite=?", (libelle, unite))
    if not row:
        row = db.one("SELECT prix_unitaire, cout_materiaux, cout_pose FROM catalogue "
                     "WHERE libelle=?", (libelle,))
    if row and float(row.get("prix_unitaire") or 0) > 0:
        return (float(row["prix_unitaire"]), float(row.get("cout_materiaux") or 0),
                float(row.get("cout_pose") or 0))
    return (float(defaut), 0.0, 0.0)


ELEC_CLE = "\u00c9lectricit\u00e9"


def prix_fourniture(libelle, unite, defaut=None):
    """Prix de la FOURNITURE (la piece seule) : bibliotheque d'abord, puis bareme."""
    row = db.one("SELECT cout_materiaux FROM catalogue WHERE libelle=? AND unite=?",
                 (libelle, unite))
    if not row:
        row = db.one("SELECT cout_materiaux FROM catalogue WHERE libelle=?", (libelle,))
    if row and float(row.get("cout_materiaux") or 0) > 0:
        return float(row["cout_materiaux"])
    if defaut is not None:
        return float(defaut)
    return float(FOURNITURE.get(libelle, 0) or 0)


def suggestions(cle_batiment, piece, surface=0.0, avec_fourniture=False):
    """Tableau de suggestions pour une pi\u00e8ce : postes de la norme, prix \u00e0 jour.

    Retourne une liste de dicts pr\u00eats pour l'\u00e9diteur : libelle, unite, quantite,
    prix_unitaire, cout_materiaux, cout_pose, norme, obligatoire, metier.
    """
    bat = TYPES_BATIMENT.get(cle_batiment) or {}
    lignes = []
    for metier in metiers_actifs():
        postes = list(postes_metier(metier, piece))
        if postes and metier == ELEC_CLE:
            postes = postes + (CABLAGE_TABLEAU
                               if piece in ("tableau", "tableau_force") else CABLAGE)
        if postes and metier == "\u00c9lectricit\u00e9" and bat.get("renovation"):
            postes = postes + ELEC_RENOVATION
        for poste in postes:
            pose, cmat, cpose = prix_pratique(poste["libelle"], poste["unite"], poste["prix"])
            fourn = 0.0
            if avec_fourniture:
                fourn = prix_fourniture(poste["libelle"], poste["unite"], poste.get("fourn"))
            lignes.append({
                "libelle": poste["libelle"],
                "unite": poste["unite"],
                "quantite": quantite_norme(poste, surface),
                "prix_pose": pose,
                "prix_fourniture": fourn,
                "prix_unitaire": pose + fourn,
                "cout_materiaux": fourn or cmat,
                "cout_pose": pose or cpose,
                "norme": poste["norme"],
                "obligatoire": bool(poste.get("obligatoire", True)),
                "metier": metier,
            })
    return lignes


def nom_piece(cle, langue="ar"):
    info = PIECES.get(cle) or {}
    return info.get(langue) or info.get("fr") or cle


def nom_batiment(cle, langue="ar"):
    info = TYPES_BATIMENT.get(cle) or {}
    return info.get(langue) or info.get("fr") or cle
