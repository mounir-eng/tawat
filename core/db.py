# -*- coding: utf-8 -*-
"""Couche donnees : schema SQLite, migrations legeres et acces bas niveau.

Aucune dependance a Streamlit : ce module est testable seul.
"""
import os
import sqlite3
import tempfile
import threading
from datetime import date

_LOCK = threading.Lock()
_CONN = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _inscriptible(dossier):
    """Vrai si on peut vraiment ecrire dans ce dossier."""
    try:
        os.makedirs(dossier, exist_ok=True)
        temoin = os.path.join(dossier, ".ecriture")
        with open(temoin, "w") as fichier:
            fichier.write("ok")
        os.remove(temoin)
        return True
    except OSError:
        return False


def _choisir_chemin():
    """Emplacement de la base : variable ARTISAN_DB, sinon dossier du logiciel.

    Sur un hebergeur (Streamlit Cloud) le dossier du code peut etre en lecture
    seule : on bascule alors vers le dossier personnel puis vers un dossier
    temporaire, afin que l'application demarre toujours.
    """
    force = os.environ.get("ARTISAN_DB")
    if force:
        if _inscriptible(os.path.dirname(os.path.abspath(force)) or "."):
            return force
    for dossier in (BASE_DIR,
                    os.path.join(os.path.expanduser("~"), ".artisan_dz"),
                    os.path.join(tempfile.gettempdir(), "artisan_dz")):
        if _inscriptible(dossier):
            return os.path.join(dossier, "artisan.db")
    return os.path.join(tempfile.gettempdir(), "artisan.db")


DB_PATH = _choisir_chemin()

SCHEMA = """
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS clients (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nom           TEXT NOT NULL,
    telephone     TEXT,
    adresse       TEXT,
    ville         TEXT,
    note          TEXT,
    date_creation TEXT DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS chantiers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nom          TEXT NOT NULL,
    client_id    INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    adresse      TEXT,
    type_travaux TEXT,
    statut       TEXT DEFAULT 'En cours',
    date_debut   TEXT,
    date_fin     TEXT,
    note         TEXT
);

CREATE TABLE IF NOT EXISTS devis_factures (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    numero      TEXT UNIQUE,
    type_doc    TEXT NOT NULL DEFAULT 'Devis',      -- Devis | Facture | Recu
    client_id   INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    chantier_id INTEGER REFERENCES chantiers(id) ON DELETE SET NULL,
    date_doc    TEXT,
    statut      TEXT DEFAULT 'Brouillon',           -- Brouillon|Envoye|Accepte|Facture|Paye|Annule
    remise      REAL DEFAULT 0,
    total       REAL DEFAULT 0,
    note        TEXT,
    echeance    TEXT,
    type_batiment TEXT,                              -- appart_neuf|villa|local|usine...
    mode_prix   TEXT DEFAULT 'pose',                 -- pose | pose_fourniture
    cree_le     TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS lignes_document (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id    INTEGER NOT NULL REFERENCES devis_factures(id) ON DELETE CASCADE,
    ordre          INTEGER DEFAULT 0,
    description    TEXT NOT NULL,
    quantite       REAL DEFAULT 1,
    unite          TEXT DEFAULT 'U',
    prix_unitaire  REAL DEFAULT 0,
    cout_materiaux REAL DEFAULT 0,   -- cout interne par unite (jamais imprime)
    cout_pose      REAL DEFAULT 0,   -- cout main d'oeuvre par unite
    total_ligne    REAL DEFAULT 0,
    piece          TEXT,            -- local concerne (Devis Express : sejour, chambre...)
    niveau         TEXT             -- etage concerne (RDC, 1er etage...) maisons et villas
);

CREATE TABLE IF NOT EXISTS paiements (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id   INTEGER REFERENCES devis_factures(id) ON DELETE CASCADE,
    chantier_id   INTEGER REFERENCES chantiers(id) ON DELETE SET NULL,
    montant       REAL NOT NULL,
    date_paiement TEXT,
    mode          TEXT DEFAULT 'Especes',
    note          TEXT
);

CREATE TABLE IF NOT EXISTS depenses_materiaux (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    chantier_id   INTEGER NOT NULL REFERENCES chantiers(id) ON DELETE CASCADE,
    libelle       TEXT NOT NULL,
    quantite      REAL DEFAULT 1,
    unite         TEXT DEFAULT 'U',
    prix_unitaire REAL DEFAULT 0,
    montant       REAL DEFAULT 0,
    fournisseur   TEXT,
    date_achat    TEXT,
    photo         TEXT
);

CREATE TABLE IF NOT EXISTS paie_main_oeuvre (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chantier_id INTEGER NOT NULL REFERENCES chantiers(id) ON DELETE CASCADE,
    ouvrier     TEXT NOT NULL,
    type_paie   TEXT DEFAULT 'Journee',
    nb_jours    REAL DEFAULT 0,
    tarif_jour  REAL DEFAULT 0,
    montant     REAL DEFAULT 0,
    date_paie   TEXT,
    note        TEXT
);

-- Bibliotheque de prix : apprend les prestations et prix reellement pratiques
CREATE TABLE IF NOT EXISTS catalogue (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle        TEXT NOT NULL,
    metier         TEXT,
    unite          TEXT DEFAULT 'U',
    prix_unitaire  REAL DEFAULT 0,
    cout_materiaux REAL DEFAULT 0,
    cout_pose      REAL DEFAULT 0,
    usages         INTEGER DEFAULT 0,
    dernier_usage  TEXT,
    UNIQUE(libelle, unite)
);

CREATE TABLE IF NOT EXISTS ouvriers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nom        TEXT NOT NULL UNIQUE,
    role       TEXT,
    tarif_jour REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS parametres (
    cle    TEXT PRIMARY KEY,
    valeur TEXT
);

CREATE INDEX IF NOT EXISTS idx_lignes_doc  ON lignes_document(document_id);
CREATE INDEX IF NOT EXISTS idx_pay_doc     ON paiements(document_id);
CREATE INDEX IF NOT EXISTS idx_pay_chant   ON paiements(chantier_id);
CREATE INDEX IF NOT EXISTS idx_mat_chant   ON depenses_materiaux(chantier_id);
CREATE INDEX IF NOT EXISTS idx_mo_chant    ON paie_main_oeuvre(chantier_id);
CREATE INDEX IF NOT EXISTS idx_doc_client  ON devis_factures(client_id);
"""

DEFAUTS = {
    "entreprise_nom": "",
    "entreprise_metier": "",
    "entreprise_tel": "",
    "entreprise_adresse": "",
    "entreprise_slogan": "",
    "marge_cible": "30",          # % de marge consideree saine
    "tarif_jour_defaut": "3000",
    "acompte_defaut": "50",       # % demande au demarrage
    "validite_devis": "30",       # jours
    "onboarding_fait": "0",
    "prefixe_devis": "DV",
}


def get_conn():
    global _CONN
    with _LOCK:
        if _CONN is None:
            _CONN = sqlite3.connect(DB_PATH, check_same_thread=False)
            _CONN.row_factory = sqlite3.Row
            _CONN.execute("PRAGMA foreign_keys = ON;")
            _CONN.executescript(SCHEMA)
            _migrer(_CONN)
            for cle, val in DEFAUTS.items():
                _CONN.execute("INSERT OR IGNORE INTO parametres (cle,valeur) VALUES (?,?)", (cle, val))
            _CONN.commit()
    return _CONN


def init():
    """Cree la base si besoin et applique les migrations douces."""
    get_conn()
    return DB_PATH


def _colonnes(conn, table):
    return {r[1] for r in conn.execute("PRAGMA table_info(%s)" % table)}


def _migrer(conn):
    """Migrations douces depuis une base creee par une version anterieure."""
    ajouts = {
        "lignes_document": [("ordre", "INTEGER DEFAULT 0"),
                            ("cout_materiaux", "REAL DEFAULT 0"),
                            ("cout_pose", "REAL DEFAULT 0"),
                            ("piece", "TEXT"),
                            ("niveau", "TEXT")],
        "devis_factures": [("echeance", "TEXT"), ("cree_le", "TEXT"),
                           ("type_batiment", "TEXT"),
                           ("mode_prix", "TEXT DEFAULT 'pose'")],
        "clients": [("ville", "TEXT")],
        "depenses_materiaux": [("photo", "TEXT")],
    }
    for table, cols in ajouts.items():
        try:
            existantes = _colonnes(conn, table)
        except sqlite3.Error:
            continue
        for nom, ddl in cols:
            if nom not in existantes:
                conn.execute("ALTER TABLE %s ADD COLUMN %s %s" % (table, nom, ddl))


# ---------------------------------------------------------------- acces court
def q(sql, params=()):
    return [dict(r) for r in get_conn().execute(sql, params).fetchall()]


def one(sql, params=()):
    r = q(sql, params)
    return r[0] if r else None


def scalar(sql, params=(), defaut=0):
    r = get_conn().execute(sql, params).fetchone()
    if r is None or r[0] is None:
        return defaut
    return r[0]


def run(sql, params=()):
    conn = get_conn()
    with _LOCK:
        cur = conn.execute(sql, params)
        conn.commit()
    return cur.lastrowid


def runmany(sql, seq):
    conn = get_conn()
    with _LOCK:
        conn.executemany(sql, seq)
        conn.commit()


# ---------------------------------------------------------------- parametres
def get_param(cle, defaut=""):
    r = one("SELECT valeur FROM parametres WHERE cle=?", (cle,))
    return r["valeur"] if r else defaut


def get_param_num(cle, defaut=0.0):
    try:
        return float(get_param(cle, defaut) or defaut)
    except (TypeError, ValueError):
        return float(defaut)


def set_param(cle, valeur):
    run("INSERT INTO parametres (cle,valeur) VALUES (?,?) "
        "ON CONFLICT(cle) DO UPDATE SET valeur=excluded.valeur", (cle, str(valeur)))


def aujourdhui():
    return date.today().isoformat()
