# Mise en ligne sur Streamlit Community Cloud

## 1. Pourquoi l'application affichait « Oh no. Error running app. »

Le fichier `.streamlit/config.toml` livré pour le PC contenait :

```toml
[server]
headless = false
port = 8501
address = "localhost"

[browser]
serverAddress = "localhost"
serverPort = 8501
```

Sur Streamlit Cloud, c'est l'hébergeur qui impose le port et l'adresse d'écoute.
En forçant `port = 8501` / `address = localhost` et `headless = false`, le serveur
n'écoutait pas où la plateforme l'attendait : dans le journal on lit exactement

```
❗ The service has encountered an error while checking the health of the
   Streamlit app: Get "http://localhost:8501/healthz": connect: connection refused
```

et le navigateur affiche alors « Oh no. Error running app. ».

Trois autres pièges ont été corrigés en même temps :

| Problème | Correction |
|---|---|
| Point d'entrée : `app.py` est **dans** le paquet et importe `artisan_pro.*` | ajout de `streamlit_app.py` à la racine du dépôt |
| `use_container_width` supprimé des versions récentes de Streamlit (le Cloud a installé la 1.63) | module `artisan_pro/ui/compat.py` : traduction automatique en `width="stretch"` |
| Dossier du code en lecture seule en ligne (`artisan.db`, `exports/`) | bascule automatique vers un dossier inscriptible (dossier personnel, puis dossier temporaire) |

## 2. Structure exacte du dépôt GitHub

```
votre-depot/
├─ streamlit_app.py         <-- « Main file path » sur Streamlit Cloud
├─ requirements.txt
├─ .gitignore
├─ .streamlit/config.toml
├─ Lancer_Artisan.bat       (usage PC uniquement)
└─ artisan_pro/
   ├─ app.py
   ├─ core/  ui/  assets/  design/  exports/
   └─ .streamlit/config.toml
```

⚠ Le dossier `artisan_pro` doit rester **un dossier**, pas être vidé à la racine.

## 3. Marche à suivre

1. Dans votre dépôt `tawat`, **supprimez tous les anciens fichiers** (surtout
   l'ancien `app.py` et l'ancien `.streamlit/config.toml`).
2. Déposez le contenu de cette archive à la racine du dépôt, puis validez
   (`Commit changes`).
3. Sur [share.streamlit.io](https://share.streamlit.io) → votre application →
   **Settings ▸ Main file path** : saisissez `streamlit_app.py`.
4. **Reboot app**. Le journal doit se terminer par `Your app is live!`.

Si une erreur subsiste : *Manage app ▸ Logs*, copiez le bloc `Traceback`
(les détails d'erreur sont désormais affichés grâce à `showErrorDetails = true`).

## 4. À savoir sur la version en ligne

* **Les données sont temporaires.** Streamlit Cloud redémarre la machine
  régulièrement : la base `artisan.db` est alors remise à zéro.
* **Tous les visiteurs partagent la même base.** L'adresse publique doit donc
  rester privée, ou l'application être limitée (Settings ▸ Sharing).
* Pour un usage professionnel réel : gardez le PC comme poste de travail, ou
  passez à une base hébergée (Postgres/Supabase) — la couche `core/db.py` est
  isolée, la migration est simple.
* Vous pouvez forcer l'emplacement de la base avec la variable d'environnement
  `ARTISAN_DB` (et celui des PDF avec `ARTISAN_EXPORTS`).

## 5. Sur PC, rien ne change

```
Lancer_Artisan.bat
```

ou bien :

```
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py --server.headless false
```
