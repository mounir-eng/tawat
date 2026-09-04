# Artisan DZ Pro \u2014 v3

Application Streamlit de gestion pour artisans du b\u00e2timent en Alg\u00e9rie :
devis, factures, re\u00e7us, chantiers, kredi (cr\u00e9dit client) et calculateurs de m\u00e9tr\u00e9.
Montants en **DZD**, **sans TVA ni fiscalit\u00e9**, donn\u00e9es 100 % locales (SQLite).

## 1. Installation (Windows / macOS / Linux)

```
pip install -r requirements.txt
```

D\u00e9pendances : `streamlit`, `pandas`, `fpdf2`.
**Aucune** d\u00e9pendance `streamlit-option-menu` : la navigation est int\u00e9gr\u00e9e.

## 2. Lancement

Le dossier doit garder le nom `artisan_pro` (c'est le nom du paquet Python).

```
cd chemin\vers\artisan_pro
streamlit run app.py
```

Premier lancement : 3 champs (nom, m\u00e9tier, t\u00e9l\u00e9phone) et l'application est pr\u00eate.

### Donn\u00e9es de d\u00e9monstration (facultatif)

```
python demo_data.py
```

## 3. Organisation des fichiers

```
artisan_pro/
  app.py                 point d'entr\u00e9e, navigation, onboarding
  core/
    db.py                SQLite : sch\u00e9ma, migrations douces, param\u00e8tres
    fmt.py               formats DZD / dates FR / liens WhatsApp, Viber, SMS
    metier.py            statuts, totaux, marges, rentabilit\u00e9, messages de relance
    catalog.py           mod\u00e8les m\u00e9tier + biblioth\u00e8que de prix apprenante
    parsing.py           \u00ab Devis \u00c9clair \u00bb : phrase -> postes
    docs.py              cr\u00e9ation, conversion, statuts, paiements
    pdf.py               PDF devis / facture / re\u00e7u (fpdf2 + polices DejaVu)
  ui/
    theme.py             jetons de design + CSS complet
    components.py        composants r\u00e9utilisables (cartes, pilules, h\u00e9ros, dialogues)
    views/               accueil, devis, chantiers, clients, kredi, calculs, r\u00e9glages
  assets/fonts/          polices Unicode embarqu\u00e9es pour les PDF
  exports/               PDF g\u00e9n\u00e9r\u00e9s
  design/maquette.html   maquette de r\u00e9f\u00e9rence du design system
  DESIGN.md              principes UI/UX, jetons, parcours
```

## 4. Base de donn\u00e9es

Fichier `artisan.db` cr\u00e9\u00e9 automatiquement \u00e0 c\u00f4t\u00e9 de `app.py`
(variable d'environnement `ARTISAN_DB` pour le d\u00e9placer).

Tables : `clients`, `chantiers`, `devis_factures`, `lignes_document`, `paiements`,
`depenses_materiaux`, `paie_main_oeuvre`, `catalogue`, `ouvriers`, `parametres`.

Formules :

- `Total = \u03a3 (quantit\u00e9 \u00d7 prix unitaire) \u2212 remise`
- `Reste \u00e0 payer = Total \u2212 \u03a3 paiements`
- `Marge devis = Total \u2212 \u03a3 quantit\u00e9 \u00d7 (co\u00fbt mat\u00e9riaux + co\u00fbt pose)`
- `B\u00e9n\u00e9fice chantier = \u03a3 encaissements \u2212 (mat\u00e9riaux + main d'\u0153uvre)`

## 5. Sauvegarde

R\u00e9glages > Donn\u00e9es : t\u00e9l\u00e9chargement du fichier `.db`, restauration, export CSV complet.

## 6. Nouveautés v8 — l'écran Devis

- **Mode de prix choisi dès le départ** : « Pose seulement » ou « Pose et fourniture ».
  En pose + fourniture, le tableau affiche la colonne **سعر القطعة** (prix de la pièce)
  et le prix unitaire devient `fourniture + pose`. La mention correspondante est
  imprimée en bas du PDF (« Prix incluant la fourniture… » / « Prix de pose uniquement… »).
- **Étages** : « منزل ذو طوابق » et « Villa » proposent Sous-sol / RDC / 1er / 2e / 3e /
  Toit. On choisit l'étage, on y ajoute ses pièces, chaque étage affiche son sous-total,
  et l'étage précède le nom de la pièce dans le PDF (« 1er étage / Chambre 2 »).
- **Nombre de pièces** : « Chambre × 3 » crée trois pièces nommées séparément
  (2 pour les enfants + 1 pour les parents), chacune avec sa propre surface.
- **Icône personnalisable** : toute pièce ajoutée porte un badge vide (+) à remplir
  depuis une palette de 20 symboles ou par saisie libre.
- **Câblage (مد الكوابل)** : câble 3G1,5 mm² et 3G2,5 mm², gaine ICTA Ø20, tirage et
  raccordement ; au tableau : 3G6, 3G10, terre 16 mm², goulotte GTL. Les longueurs se
  calculent au mètre linéaire selon la surface de la pièce.
- **Fenêtres de dialogue** limitées à 560 px : elles ne prennent plus toute la largeur.
- **Suggestions strictement métier** : un électricien ne voit que des postes
  d'électricité (norme NF C 15-100), un peintre ne voit jamais de câblage.

Colonnes ajoutées : `lignes_document.niveau` et `devis_factures.mode_prix`
(migration automatique d'une base existante au démarrage).

---

## 7. Nouveautés v9 — icônes au même gabarit + ajout des pièces en une fois

### 7.1 Icônes toutes à la même taille

* Chaque tuile (bâtiment, mode de prix, pièce) affiche désormais son icône dans une
  **boîte de hauteur fixe (38 px, 27 px de police)** : toutes les icônes ont
  exactement la même taille, quelle que soit la pièce.
* **Le texte rétrécit tout seul** quand le libellé est long :
  * jusqu'à 12 caractères → 13,5 px ;
  * de 13 à 19 caractères → 11,8 px ;
  * au-delà de 19 caractères (ex. « اللوحة الكهربائية والأرضي ») → 10,4 px.
  Les tuiles gardent ainsi la même hauteur et le texte ne déborde plus.
* **Icônes remplacées** : les emoji trop récents (2018-2020) s'affichaient en carré
  vide ou en mauvais dessin sur Windows. Remplaçants retenus :
  couloir → ممر (piéton), escalier → flèche haut, sous-sol → flèche bas,
  buanderie → goutte, balcon → feuillage, vitrine → magasin,
  surface de vente → chariot, vestiaire → vêtement, local technique → engrenage,
  hall de production → usine, bureau fermé → écran.
* La palette de personnalisation propose **20 icônes sûres** + saisie libre.

### 7.2 Ajout des pièces en une seule fois (couchage / nombre)

1. Écran « القطع » : chaque tuile porte un **compteur − / +** (0 à 12).
   On règle par exemple 3 chambres, 1 cuisine, 1 séjour, 2 WC.
2. Un bandeau récapitule la sélection, puis **un seul bouton**
   « أضف القطع المحددة (N) » ajoute **toutes les pièces d'un coup**.
3. Les pièces se posent **en liste, les unes sous les autres**, déjà chiffrées
   selon la norme NF C 15-100 et numérotées (غرفة نوم 1, 2, 3…), rattachées à
   l'étage courant.
4. Chaque carte affiche un état : **« بانتطار التخصيص »** puis
   **« ✓ مخصّصة »**. Le bouton **« تخصيص »** ouvre le panneau (icône, nom,
   surface, tableau des travaux) et **« حفط والقطعة الموالية › »** enchaîne
   directement sur la pièce suivante non encore personnalisée.
5. Les compteurs se remettent à zéro après l'ajout : on peut enrichir un autre
   étage sans effacer le travail déjà fait (la numérotation continue).

### 7.3 Contrôle qualité

46 vérifications automatiques v9 (en plus des 46 de la v8) : gabarit d'icône,
réduction automatique du texte, icônes compatibles Windows, ajout de 4 pièces en
un clic, numérotation, pré-chiffrage, remise à zéro des compteurs, état
« personnalisée », enchaînement pièce suivante, enregistrement et PDF.
