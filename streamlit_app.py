# -*- coding: utf-8 -*-
"""Point d'entree unique de l'application.

  * Streamlit Community Cloud : mettre "streamlit_app.py" dans
    "Main file path" au moment du deploiement.
  * PC (Windows) : double-cliquer sur Lancer_Artisan.bat, ou bien
    "python -m streamlit run streamlit_app.py".

Ce fichier ne contient aucune logique : il ajoute le dossier du depot au chemin
Python puis lance le paquet artisan_pro (dossier du meme nom, a cote).
"""
import os
import sys

RACINE = os.path.dirname(os.path.abspath(__file__))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

import streamlit as st  # noqa: E402

try:
    from artisan_pro import app  # noqa: F401,E402  (l'import demarre l'application)
except ModuleNotFoundError as erreur:
    st.error(
        "Le dossier **artisan_pro** est introuvable a la racine du depot.\n\n"
        "Structure attendue :\n\n"
        "```\n"
        "votre-depot/\n"
        "  streamlit_app.py\n"
        "  requirements.txt\n"
        "  artisan_pro/\n"
        "      app.py\n"
        "      core/ ui/ assets/\n"
        "```\n\n"
        "Detail technique : %s" % erreur)
    st.stop()
