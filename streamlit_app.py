# -*- coding: utf-8 -*-
"""Alias du point d'entree.

L'application est dans app.py, a cote de ce fichier. Ce raccourci existe
uniquement pour que "Main file path" fonctionne sur Streamlit Cloud, que vous
saisissiez app.py OU streamlit_app.py.
"""
import os
import sys

RACINE = os.path.dirname(os.path.abspath(__file__))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

import app  # noqa: F401,E402  (l'import demarre l'application)
