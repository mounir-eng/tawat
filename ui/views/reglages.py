# -*- coding: utf-8 -*-
"""R\u00e9glages : identit\u00e9 de l'entreprise, r\u00e8gles commerciales, donn\u00e9es et sauvegarde."""
import io
import os
import shutil
import zipfile
from datetime import datetime

import streamlit as st

from core import catalog, db
from core.fmt import dz, nombre
from .. import components as c


def afficher():
    c.entete(c.bi("\u0627\u0644\u0625\u0639\u062f\u0627\u062f\u0627\u062a", "R\u00e9glages"),
             c.bi("\u0645\u0624\u0633\u0633\u062a\u0643 \u0648\u0642\u0648\u0627\u0639\u062f \u0627\u0644\u062d\u0633\u0627\u0628", "votre entreprise et vos r\u00e8gles"))
    onglets = st.tabs(["\U0001f3e0 Entreprise", "\U0001f4b0 R\u00e8gles", "\U0001f4be Donn\u00e9es"])

    with onglets[0]:
        with st.container(border=True):
            nom = st.text_input("Nom de l'entreprise / artisan", value=db.get_param("entreprise_nom"),
                                key="rg_nom", placeholder="Ets. Ma\u00efz \u2014 Peinture & Rev\u00eatement")
            les_metiers = list(catalog.CORRESPONDANCE_METIER.keys())
            metier_actuel = db.get_param("entreprise_metier")
            index_metier = (les_metiers.index(metier_actuel) if metier_actuel in les_metiers
                            else len(les_metiers) - 1)
            metier = st.selectbox(c.bi("\u0645\u0647\u0646\u062a\u0643", "M\u00e9tier"), les_metiers,
                                  index=index_metier, key="rg_metier")
            st.caption(c.bi("\u064a\u062d\u062f\u062f \u0627\u0644\u0646\u0645\u0627\u0630\u062c \u0648\u0627\u0644\u0627\u0642\u062a\u0631\u0627\u062d\u0627\u062a \u0627\u0644\u062a\u064a \u062a\u0638\u0647\u0631 \u0644\u0643 \u0623\u0648\u0644\u0627",
                            "D\u00e9termine les mod\u00e8les et suggestions affich\u00e9s en premier."))
            type_compte = st.selectbox(c.bi("\u0646\u0648\u0639 \u0627\u0644\u062d\u0633\u0627\u0628", "Type de compte"),
                                       [c.bi("\u0635\u0627\u062d\u0628 \u0635\u0646\u0639\u0629", "Artisan"),
                                        c.bi("\u0645\u0642\u0627\u0648\u0644", "Entrepreneur")],
                                       index=0 if db.get_param("type_compte") != "entrepreneur" else 1,
                                       key="rg_type")
            col1, col2 = st.columns(2)
            tel = col1.text_input("T\u00e9l\u00e9phone", value=db.get_param("entreprise_tel"), key="rg_tel")
            ville = col2.text_input("Ville", value=db.get_param("entreprise_ville"), key="rg_ville")
            adresse = st.text_input("Adresse", value=db.get_param("entreprise_adresse"), key="rg_adr")
            rib = st.text_input("CCP / RIB (affich\u00e9 sur les documents)",
                                value=db.get_param("entreprise_rib"), key="rg_rib")
            mentions = st.text_area("Mentions bas de page", value=db.get_param("mentions"),
                                    key="rg_mentions",
                                    help="Ex. Devis valable 30 jours \u2014 acompte 50 %% \u00e0 la commande.")
            if st.button("Enregistrer", type="primary", use_container_width=True):
                db.set_param("entreprise_nom", nom)
                db.set_param("entreprise_metier", metier)
                db.set_param("type_compte",
                             "artisan" if type_compte.endswith("(Artisan)") else "entrepreneur")
                db.set_param("entreprise_tel", tel)
                db.set_param("entreprise_ville", ville)
                db.set_param("entreprise_adresse", adresse)
                db.set_param("entreprise_rib", rib)
                db.set_param("mentions", mentions)
                c.toast("R\u00e9glages enregistr\u00e9s")
                st.rerun()
        st.caption("Ces informations apparaissent en haut de chaque devis, facture et re\u00e7u PDF.")

    with onglets[1]:
        with st.container(border=True):
            marge = st.slider("Marge cible (%)", 5, 60, int(db.get_param_num("marge_cible", 30)),
                              key="rg_marge")
            st.caption("En dessous de la moiti\u00e9 de cette cible, la pastille de marge passe "
                       "en orange puis en rouge.")
            acompte = st.slider("Acompte conseill\u00e9 (%)", 0, 100,
                                int(db.get_param_num("acompte_defaut", 50)), key="rg_acompte")
            col1, col2 = st.columns(2)
            tarif = col1.number_input("Tarif journalier ouvrier (DZD)", min_value=0.0, step=500.0,
                                      value=db.get_param_num("tarif_jour_defaut", 3000),
                                      key="rg_tarif")
            validite = col2.number_input("Validit\u00e9 des devis (jours)", min_value=1, step=1,
                                         value=int(db.get_param_num("validite_devis", 30)),
                                         key="rg_valid")
            echeance = st.number_input("D\u00e9lai de paiement des factures (jours)", min_value=0, step=1,
                                       value=int(db.get_param_num("delai_paiement", 15)),
                                       key="rg_ech")
            if st.button("Enregistrer les r\u00e8gles", type="primary", use_container_width=True):
                db.set_param("marge_cible", marge)
                db.set_param("acompte_defaut", acompte)
                db.set_param("tarif_jour_defaut", tarif)
                db.set_param("validite_devis", validite)
                db.set_param("delai_paiement", echeance)
                c.toast("R\u00e8gles mises \u00e0 jour")
                st.rerun()

        with st.container(border=True):
            st.markdown('<div class="sec" style="margin-top:0">\u00c9quipe</div>',
                        unsafe_allow_html=True)
            ouvriers = db.q("SELECT * FROM ouvriers ORDER BY nom")
            for o in ouvriers:
                col1, col2, col3 = st.columns([2, 1.2, 1])
                col1.markdown('<div class="nm" style="padding-top:8px">%s</div>' % c.e(o["nom"]),
                              unsafe_allow_html=True)
                nouveau_tarif = col2.number_input("Tarif/jour", min_value=0.0, step=500.0,
                                                  value=float(o["tarif_jour"] or 0),
                                                  key="ouv_%d" % o["id"], label_visibility="collapsed")
                if nouveau_tarif != float(o["tarif_jour"] or 0):
                    db.run("UPDATE ouvriers SET tarif_jour=? WHERE id=?", (nouveau_tarif, o["id"]))
                if col3.button("Retirer", key="delouv_%d" % o["id"], use_container_width=True):
                    db.run("DELETE FROM ouvriers WHERE id=?", (o["id"],))
                    st.rerun()
            nom_ouvrier = st.text_input("Ajouter un ouvrier", key="rg_ouv_nom",
                                        placeholder="Nom du ma\u00e7on, manoeuvre, t\u00e2cheron\u2026")
            if st.button("\uff0b Ajouter \u00e0 l'\u00e9quipe", use_container_width=True,
                         disabled=not nom_ouvrier.strip()):
                db.run("INSERT OR IGNORE INTO ouvriers (nom,tarif_jour) VALUES (?,?)",
                       (nom_ouvrier.strip(), db.get_param_num("tarif_jour_defaut", 3000)))
                st.rerun()

    with onglets[2]:
        stats = {
            "Clients": db.scalar("SELECT COUNT(*) FROM clients"),
            "Chantiers": db.scalar("SELECT COUNT(*) FROM chantiers"),
            "Documents": db.scalar("SELECT COUNT(*) FROM devis_factures"),
            "Prestations apprises": db.scalar("SELECT COUNT(*) FROM catalogue"),
        }
        with st.container(border=True):
            st.markdown('<div class="sec" style="margin-top:0">Votre base</div>',
                        unsafe_allow_html=True)
            for libelle, valeur in stats.items():
                c.ligne_stat(libelle, nombre(valeur or 0))
            st.caption("Fichier : %s" % db.DB_PATH)

        with st.container(border=True):
            st.markdown('<div class="sec" style="margin-top:0">%s</div>'
                        % c.bi("\u0645\u0643\u062a\u0628\u0629 \u0627\u0644\u0623\u0633\u0639\u0627\u0631", "Biblioth\u00e8que de prix"),
                        unsafe_allow_html=True)
            st.caption(c.bi("%d \u062e\u062f\u0645\u0629 \u0645\u0633\u062c\u0644\u0629", "%d prestations en biblioth\u00e8que",
                            db.scalar("SELECT COUNT(*) FROM catalogue") or 0))
            if st.button(c.bi("\U0001f504 \u062d\u0645\u0651\u0644 \u0645\u0643\u062a\u0628\u0629 \u0645\u0647\u0646\u062a\u064a \u0645\u0646 \u062c\u062f\u064a\u062f",
                              "Recharger la biblioth\u00e8que m\u00e9tier"), use_container_width=True):
                insere = catalog.ensemencer(catalog.metiers_artisan() or None)
                c.toast(c.bi("%d \u062e\u062f\u0645\u0629 \u062c\u062f\u064a\u062f\u0629", "%d nouvelles prestations", insere))
                st.rerun()
            metier_import = st.selectbox(c.bi("\u0645\u064a\u062f\u0627\u0646 \u0627\u0644\u0627\u0633\u062a\u064a\u0631\u0627\u062f", "M\u00e9tier de la liste"),
                                         list(catalog.TEMPLATES.keys()), key="imp_metier")
            fichier = st.file_uploader(c.bi("\u0645\u0644\u0641 \u0623\u0633\u0639\u0627\u0631 Excel \u0623\u0648 CSV",
                                            "Liste de prix (Excel .xlsx ou CSV)"),
                                       type=["xlsx", "csv"], key="imp_fichier")
            if fichier is not None and st.button(c.bi("\u2b07\ufe0f \u0627\u0633\u062a\u0648\u0631\u062f \u0627\u0644\u0622\u0646", "Importer"),
                                                 type="primary", use_container_width=True):
                try:
                    compte = catalog.importer_prix(fichier, metier_import)
                    c.toast(c.bi("\u062a\u0645 \u0627\u0633\u062a\u064a\u0631\u0627\u062f %d \u062e\u062f\u0645\u0629",
                                 "%d prestations import\u00e9es", compte))
                    st.rerun()
                except Exception as exc:
                    st.error("Import impossible : %s" % exc)

        with st.container(border=True):
            st.markdown('<div class="sec" style="margin-top:0">Sauvegarde</div>',
                        unsafe_allow_html=True)
            if os.path.exists(db.DB_PATH):
                with open(db.DB_PATH, "rb") as fichier:
                    st.download_button(
                        "\u2b07\ufe0f T\u00e9l\u00e9charger la sauvegarde", fichier.read(),
                        file_name="artisan-%s.db" % datetime.now().strftime("%Y%m%d"),
                        mime="application/octet-stream", use_container_width=True, type="primary")
            envoi = st.file_uploader("Restaurer une sauvegarde (.db)", type=["db"], key="rg_restore")
            if envoi is not None and st.button("Restaurer maintenant", use_container_width=True):
                shutil.copy(db.DB_PATH, db.DB_PATH + ".avant-restauration")
                with open(db.DB_PATH, "wb") as sortie:
                    sortie.write(envoi.getbuffer())
                c.toast("Sauvegarde restaur\u00e9e")
                st.rerun()

        with st.container(border=True):
            st.markdown('<div class="sec" style="margin-top:0">Export Excel / CSV</div>',
                        unsafe_allow_html=True)
            st.download_button("\u2b07\ufe0f Exporter tout en CSV (zip)", _zip_csv(),
                               file_name="export-artisan.zip", mime="application/zip",
                               use_container_width=True)


def _zip_csv():
    import csv
    tampon = io.BytesIO()
    tables = ["clients", "chantiers", "devis_factures", "lignes_document", "paiements",
              "depenses_materiaux", "paie_main_oeuvre", "catalogue"]
    with zipfile.ZipFile(tampon, "w", zipfile.ZIP_DEFLATED) as archive:
        for table in tables:
            lignes = db.q("SELECT * FROM %s" % table)
            texte = io.StringIO()
            if lignes:
                writer = csv.DictWriter(texte, fieldnames=list(lignes[0].keys()))
                writer.writeheader()
                writer.writerows(lignes)
            archive.writestr("%s.csv" % table, texte.getvalue())
    return tampon.getvalue()
