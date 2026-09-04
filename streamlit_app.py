# -*- coding: utf-8 -*-
"""Point d'entree de l'application (Streamlit Cloud ou PC).

A RETENIR : Streamlit relance ce script a CHAQUE interaction, alors qu'un
module importe (app.py) n'est charge qu'une seule fois. Se contenter d'un
"import app" n'affiche donc rien a partir de la deuxieme execution : c'est ce
qui produisait un ecran blanc en ligne. On importe la fonction, puis on
l'appelle explicitement a chaque execution.
"""
import os
import sys
import traceback

RACINE = os.path.dirname(os.path.abspath(__file__))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

import streamlit as st  # noqa: E402

try:
    from app import main
except Exception:  # jamais d'ecran blanc muet : on montre la cause
    st.error("Le chargement de l'application a echoue.")
    st.code(traceback.format_exc())
    st.caption("Verifiez que les dossiers core/ et ui/ sont bien a la racine "
               "du depot, a cote de app.py.")
    st.stop()

main()
