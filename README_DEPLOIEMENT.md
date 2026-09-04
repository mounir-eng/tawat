# Mise en ligne sur Streamlit Community Cloud

## 1. Structure : tout est à la racine

Le contenu de l'archive se dépose **directement** à la racine du dépôt GitHub,
sans dossier intermédiaire :

```
votre-depot/
├─ app.py                 <-- l'application (Main file path)
├─ streamlit_app.py       <-- alias : marche aussi comme Main file path
├─ requirements.txt
├─ .gitignore
├─ Lancer_Artisan.bat     (PC Windows)
├─ .streamlit/config.toml
├─ core/                  logique métier (base, PDF, normes NF C 15-100...)
├─ ui/                    interface (thème, composants, écrans)
├─ assets/fonts/          polices des PDF (à conserver !)
├─ design/  exports/
└─ demo_data.py           jeu de démonstration (optionnel)
```

## 2. Marche à suivre

1. Dans le dépôt `tawat`, **supprimez tous les anciens fichiers** (surtout
   l'ancien `app.py`, l'ancien `.streamlit/config.toml` et un éventuel dossier
   `artisan_pro`).
2. `Add file ▸ Upload files` : glissez **tout le contenu de l'archive**
   (les dossiers `core`, `ui`, `assets`, `design`, `exports`, `.streamlit` et
   les fichiers de la racine), puis `Commit changes`.
3. Sur [share.streamlit.io](https://share.streamlit.io) → votre application →
   **Settings ▸ Main file path** : `app.py` (ou `streamlit_app.py`).
4. **Reboot app**. Le journal doit se terminer par `Your app is live!`.

> GitHub n'accepte pas les dossiers vides : si `exports/` disparaît à l'upload,
> ce n'est pas grave, l'application le recrée toute seule.

## 3. Ce qui empêchait le démarrage en ligne (corrigé)

| Cause | Correction |
|---|---|
| `.streamlit/config.toml` forçait `headless = false`, `port = 8501`, `address = localhost` — or c'est l'hébergeur qui impose le port → `healthz : connection refused` puis « Oh no. Error running app. » | configuration compatible Cloud ; les options d'adresse/port sont passées en ligne de commande par `Lancer_Artisan.bat` sur PC |
| Le code vivait dans un paquet `artisan_pro` alors que le fichier principal était `app.py` à la racine | structure à plat : `app.py`, `core/`, `ui/` à la racine |
| Le Cloud installe Streamlit 1.63, où `use_container_width` n'existe plus | `ui/compat.py` traduit automatiquement en `width="stretch"` (aucun effet sur votre PC) |
| Dossier du code en lecture seule en ligne (`artisan.db`, `exports/`) | bascule automatique vers un dossier inscriptible |

Si une erreur subsiste : *Manage app ▸ Logs*, copiez le bloc `Traceback`
(les détails d'erreur sont affichés grâce à `showErrorDetails = true`).

## 4. À savoir sur la version en ligne

* **Données temporaires** : Streamlit Cloud redémarre la machine régulièrement,
  la base `artisan.db` est alors remise à zéro.
* **Base partagée** : tous les visiteurs voient les mêmes devis. Gardez
  l'adresse privée (Settings ▸ Sharing) tant qu'il n'y a pas de comptes.
* Emplacements personnalisables : variables `ARTISAN_DB` et `ARTISAN_EXPORTS`.
* Pour un usage professionnel durable : PC comme poste de travail, ou base
  hébergée (Postgres/Supabase) — `core/db.py` est isolé, la migration est simple.

## 5. Sur PC

```
Lancer_Artisan.bat
```

ou :

```
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.headless false
```
