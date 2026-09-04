# Artisan DZ Pro \u2014 Design system & partis pris UI/UX

## 1. Principes

1. **Un \u00e9cran = une d\u00e9cision.** Chaque page r\u00e9pond \u00e0 une seule question :
   \u00ab combien j'ai gagn\u00e9 ce mois ? \u00bb, \u00ab qui me doit de l'argent ? \u00bb, \u00ab ce devis est-il rentable ? \u00bb.
2. **Le chiffre d'abord.** Les montants sont en chiffres tabulaires, gras, align\u00e9s \u00e0 droite ;
   le texte explicatif est secondaire et gris.
3. **Jamais de page blanche.** Chaque liste vide propose l'action suivante
   (mod\u00e8le m\u00e9tier, cr\u00e9ation de client, premi\u00e8re d\u00e9pense).
4. **Le priv\u00e9 reste priv\u00e9.** Les co\u00fbts internes (mat\u00e9riaux, pose) sont dans un bloc ambre
   \u00ab non visible par le client \u00bb, repli\u00e9 par d\u00e9faut, jamais imprim\u00e9 sur le PDF.
5. **Pouce d'abord.** Cibles tactiles \u2265 44 px, navigation fixe en bas, actions primaires
   dans une barre coll\u00e9e au bas de l'\u00e9diteur.
6. **Z\u00e9ro jargon comptable.** \u00ab Kredi \u00bb, \u00ab reste \u00e0 payer \u00bb, \u00ab journ\u00e9e ouvrier \u00bb :
   le vocabulaire du chantier, pas celui du cabinet comptable.

## 2. Jetons

| R\u00f4le | Valeur |
| --- | --- |
| Fond | `#FFFFFF` |
| Fond doux | `#F9F8F7` |
| Surface secondaire | `#F0EFED` |
| Bordure | `#E6E5E3` |
| Texte | `#2C2C2B` |
| Texte secondaire | `#7D7A75` |
| Encre (h\u00e9ros) | `#1B2431` \u2192 `#243447` |
| Bleu (action) | `#2783DE` / fond `#E5F2FC` |
| Vert (sain, encaiss\u00e9) | `#46A171` / fond `#E8F1EC` |
| Ambre (attention, priv\u00e9) | `#D5803B` / fond `#FBEBDE` |
| Rouge (retard, perte) | `#E56458` / fond `#FCE9E7` |
| Neutre ouvriers | `#8C8880` |

Rayons : 8 / 11 / 12 / 14 / 16 px \u00b7 Ombre : `0 1px 2px rgba(0,0,0,.05), 0 4px 12px rgba(0,0,0,.04)`.

## 3. Composants

- **H\u00e9ros encre** : KPI principal + 2 \u00e0 3 cases secondaires (mois, chantier, kredi).
- **Pilule de statut** : Brouillon / Envoy\u00e9 / Accept\u00e9 / Factur\u00e9 / Pay\u00e9, couleur port\u00e9e par le sens.
- **Barre de r\u00e9partition** : une seule barre segment\u00e9e mat\u00e9riaux / ouvriers / b\u00e9n\u00e9fice,
  plus lisible qu'un camembert sur un t\u00e9l\u00e9phone.
- **Carte document** : num\u00e9ro, client, chantier, date, nombre de postes, total, reste \u00e0 payer.
- **Avatar initiales** color\u00e9 par l'\u00e9tat du client (bleu \u00e0 jour, rouge en retard).
- **Dialogues** natifs (`st.dialog`) avec repli automatique si la version de Streamlit est ancienne.
- **\u00c9tats vides** illustr\u00e9s + action directe.

## 4. Parcours cl\u00e9s

### Cr\u00e9er un devis (3 chemins)

1. **Mod\u00e8les m\u00e9tier cumulables** \u2014 8 mod\u00e8les (peinture, ma\u00e7onnerie, plomberie, \u00e9lectricit\u00e9,
   pl\u00e2tre, carrelage, salle de bain, \u00e9tanch\u00e9it\u00e9). On peut en cocher plusieurs : les postes
   s'additionnent, les prix sont ceux **d\u00e9j\u00e0 pratiqu\u00e9s** par l'artisan.
2. **Devis \u00c9clair** \u2014 une phrase dict\u00e9e (\u00ab 45 m2 peinture 550 + 12 prises 2800 \u00bb) est
   convertie en postes structur\u00e9s.
3. **Devis vierge** \u2014 pour les cas particuliers.

### \u00c9diter un devis

Marge pr\u00e9visionnelle en direct en haut (montant, %, pastille sant\u00e9, barre co\u00fbt/marge),
postes en cartes, co\u00fbts internes repli\u00e9s, marge par ligne, remise en montant ou %,
\u00ab arrondir au millier \u00bb, acompte conseill\u00e9 calcul\u00e9, barre d'action fixe
(Enregistrer / PDF / Envoyer).

### Encaisser et relancer

\u00c9cran Kredi tri\u00e9 par anciennet\u00e9 : \u00e2ge de la dette, part d\u00e9j\u00e0 vers\u00e9e, et surtout un
**ton de relance progressif** (doux avant 7 jours, normal, ferme au-del\u00e0 de 30 jours),
en fran\u00e7ais ou en darija, envoy\u00e9 en un tap vers WhatsApp, Viber ou SMS.

### Suivre un chantier

B\u00e9n\u00e9fice net en h\u00e9ros, r\u00e9partition en barre, saisie d'une d\u00e9pense en 3 gestes,
pointage d'une journ\u00e9e ouvrier avec tarif m\u00e9moris\u00e9 par personne.

### Calculer

Carrelage, peinture, ma\u00e7onnerie, b\u00e9ton, pl\u00e2tre et chape : le r\u00e9sultat n'est pas une
impasse, il se transforme en **poste de devis** (nouveau devis ou devis existant).

## 5. Innovations

- **Biblioth\u00e8que de prix apprenante** : chaque devis enregistr\u00e9 met \u00e0 jour le prix de r\u00e9f\u00e9rence
  d'une prestation ; les mod\u00e8les m\u00e9tier se calibrent tout seuls.
- **Marge priv\u00e9e en direct**, ligne par ligne et globale, avec alerte visuelle sous l'objectif.
- **Relances \u00e0 ton progressif** bilingues FR / darija.
- **Devis \u00c9clair** : saisie en langage naturel adapt\u00e9e au vocabulaire du b\u00e2timent alg\u00e9rien.
- **Passerelle calcul \u2192 devis** : le m\u00e9tr\u00e9 devient une ligne factur\u00e9e sans re-saisie.
- **Sauvegarde et export CSV** en un bouton, sans compte ni cloud.

## 6. Refonte visuelle v8

- **Palette approfondie** : encre indigo `#1B2559`, accent en dégradé `#2D5BFF → #6E8BFF`,
  fonds radiaux bleu et menthe, ombres à deux couches, rayons de 14 à 20 px.
- **Rail de progression** en 3 étapes (Client / Pièces / Envoi) : étape faite en vert avec
  coche, étape en cours en bleu, et pastille de **total en direct** à droite du rail.
- **Tuiles hautes** (104 → 120 px) : grosse icône, libellé arabe en gras, libellé français
  en dessous ; survol qui soulève la carte ; sélection en dégradé clair encadré de bleu
  (le texte reste lisible, contrairement à un bouton bleu plein).
- **Panneau d'ajout intégré à la page** (plus de fenêtre modale) : badge d'icône, nom,
  nombre de pièces et surface sur une seule ligne, puis le vrai tableau éditable.
- **Cartes de pièce** à filet coloré, badge d'icône, sous-titre (nb de travaux, m², étage)
  et montant aligné à droite en chiffres tabulaires.
- **Bandeaux d'étage** avec sous-total, et **total du panneau** sur bandeau nuit dégradé
  détaillant la part fourniture et la part pose.
- **Dialogues contraints à 560 px** (94 vw maxi sur téléphone), coins 20 px, ombre portée.

---

## 7. v9 — Gabarit d'icône unique & ajout par lot

### 7.1 Grille de tuiles (`.dx-t`)

| Élément | Règle |
|---|---|
| Boîte d'icône `.ico` | hauteur **38 px** fixe, police **27 px**, `overflow:hidden` → toutes les icônes identiques |
| Libellé arabe `.nm` | 13,5 px · `min-height:34px` · centré en flex |
| `.nm.sm` | 11,8 px — déclenché à partir de 13 caractères |
| `.nm.xs` | 10,4 px, `letter-spacing:-.2px` — à partir de 20 caractères |
| Sous-titre `.fr` | 10,5 px gris, une seule ligne avec ellipse |
| Conteneur | `st-key-dxbox_*` (bâtiment / mode) et `st-key-dxtile_*` (pièce) : carte blanche, rayon 18 px, ombre douce, `translateY(-2px)` au survol |
| État sélectionné | suffixe `_on_` → bordure bleue `--bleu`, dégradé bleuté, ombre colorée |
| Mobile (≤ 640 px) | icône 32 px, sous-titre masqué, 2 colonnes |

L'icône est rendue en **HTML au-dessus du bouton** (et non dans son libellé) :
c'est ce qui garantit un gabarit strictement identique, indépendamment de la
longueur du texte et du moteur de rendu de Streamlit.

### 7.2 Sélection quantitative

* Compteur `st.number_input` **dans la tuile** (0 → 12), chiffre centré, gras,
  couleur indigo ; la tuile s'allume dès que le compteur dépasse 0.
* Bandeau `.dx-lot` : pastille dégradée avec le total sélectionné + rappel
  « 🛏️ غرفة نوم ×3 · 🍳 المطبخ ×1 ».
* Bouton d'ajout unique (46 px, plein) dans `st-key-dx_addbar`.
* Cartes de pièces : badge `.bg` gris « بانتطار التخصيص » → badge vert
  `.bg.ok` « ✓ مخصّصة » ; le bouton « تخصيص » reste en bleu plein tant que la
  pièce n'a pas été revue.

### 7.3 Icônes sûres

Règle typographique retenue : **aucun emoji des blocs 2018-2020**
(`U+1FA70–U+1FAFF`, `U+1F6D5–U+1F6DF`), non couverts par Segoe UI Emoji sur les
Windows installés chez les artisans. Une vérification automatique bloque toute
régression sur ce point.


---

# v13 \u2014 Refonte visuelle bilingue + architecture multipage

## 1. Libell\u00e9s bilingues verticaux (`ui/champs.py`)

Avant : `"\u0627\u0644\u0627\u0633\u0645 / Nom"` sur une seule ligne (illisible, coup\u00e9 sur t\u00e9l\u00e9phone).
Apr\u00e8s : un bloc `.lab2` par champ \u2014 **arabe en gras au-dessus**, fran\u00e7ais en
sous-titre gris plus petit, ic\u00f4ne \u00e0 gauche, ast\u00e9risque rouge si obligatoire,
bulle `?` si aide.

```
champs.texte("\u0627\u0644\u0627\u0633\u0645", "Nom du client", requis=True, icone="\U0001f464", key="cl_nom")
```

Tous les widgets passent par le m\u00eame moteur (`label_visibility="collapsed"` +
HTML du libell\u00e9) : `texte`, `zone`, `nombre`, `montant`, `choix`, `multi`,
`radio`, `segments`, `bascule`, `date_`, `wilaya`.

## 2. Options de s\u00e9lecteurs format\u00e9es (`core/wilayas.py`)

Les 58 wilayas sont stock\u00e9es par **code num\u00e9rique** et affich\u00e9es
`"[16] \u0627\u0644\u062c\u0632\u0627\u0626\u0631 - Alger"` via `format_func`. `champs.wilaya()` retourne donc un entier
(stable en base), jamais une cha\u00eene de caract\u00e8res. Les clients sont list\u00e9s
de la m\u00eame fa\u00e7on : `"[01] Ammi Salah"`.

## 3. Listings en cartes CSS (`ui/cartes.py`)

Une grille `.karts` en `auto-fill / minmax(296px, 1fr)` : 3 colonnes sur PC,
2 sur tablette, 1 sur t\u00e9l\u00e9phone. Chaque carte porte : avatar \u00e0 initiales,
nom arabe + nom latin, note en \u00e9toiles, badge de disponibilit\u00e9, tags
m\u00e9tier / wilaya, tarif, puis **trois actions** :

| Action | Lien | Inactif si |
|---|---|---|
| Appeler | `tel:+213\u2026` | num\u00e9ro vide |
| WhatsApp | `wa.me/213\u2026` + message pr\u00e9-r\u00e9dig\u00e9 | num\u00e9ro vide |
| BaridiMob | WhatsApp + RIP et montant | RIP absent (R\u00e9glages) |

**Performance** : toute la grille est rendue en **un seul appel HTML**, pas un
widget Streamlit par ligne. Le clic sur une carte ouvre la fiche via un lien
interne `?fiche=<id>`.

## 4. Navigation multipage (`ui/routes.py`)

10 pages d\u00e9clar\u00e9es avec `st.Page`, group\u00e9es en 4 sections par
`st.navigation` : Atelier \u00b7 R\u00e9seau \u00b7 Argent \u00b7 Outils. Chaque page a sa
propre URL. Repli automatique sur l'ancien routeur si la version de Streamlit
install\u00e9e est plus ancienne (`routes.moderne()`), plus une barre d'onglets
basse sur t\u00e9l\u00e9phone.

## 5. M\u00e9moire d'\u00e9cran (`ui/etat.py`)

Probl\u00e8me Streamlit : la valeur d'un widget dispara\u00eet de `session_state` d\u00e8s
qu'il n'est plus affich\u00e9. Solution : un magasin durable `f:<\u00e9cran>:<champ>`
aliment\u00e9 par `on_change`, plus `p:<\u00e9cran>` pour la fiche ouverte. R\u00e9sultat :
recherche, m\u00e9tier, wilaya, tri et filtre \u00ab disponibles \u00bb sont retrouv\u00e9s
intacts au retour sur la page, et le compteur \u00ab X filtres \u00bb pilote le bouton
de remise \u00e0 z\u00e9ro.

## 6. Typographie (`ui/theme.py`, `CSS_V12`)

`Cairo` pour l'arabe (`--pol-ar`), `Inter` pour le latin (`--pol-fr`), zones
tactiles de 44 px (`--h-ch`), rayons de 12 px, colonnes align\u00e9es par le bas,
et une section `@media (max-width:640px)` qui passe en une colonne et masque
les sous-titres des boutons d'action.


---

## v14 - Coquille mobile-first (abandon du plein ecran bureau)

L'application n'est plus une page web large avec un menu lateral : c'est une
application telephone, centree, meme sur un grand ecran.

### 1. Canevas etroit et centre

| Jeton | Valeur | Role |
| --- | --- | --- |
| `--canevas` | `650px` | largeur maximale du contenu, centree (`margin: auto`) |
| `--r-carte` | `16px` | rayon de toutes les cartes |
| `--pad-carte` | `12px` | padding interieur serre |
| `--h-act` | `40px` | hauteur des boutons d'action |
| `--sh-doux` | `0 1px 2px / 0 6px 16px` | ombre discrete des cartes |
| `--sh-flott` | ombre large | "telephone pose sur la table" (>= 900 px) |

- `.block-container` et `[data-testid="stMainBlockContainer"]` sont limites a
  `var(--canevas)` avec un padding de `0.55rem 0.85rem 4.2rem`.
- Au-dela de 900 px de large, la colonne prend un fond blanc, un rayon de 26 px
  et une ombre flottante : l'effet "maquette de telephone" sans iframe.
- La barre laterale est totalement supprimee (`stSidebar`, `stSidebarNav`,
  `collapsedControl`), l'en-tete Streamlit devient transparent (2,2 rem).

### 2. Navigation : barre d'application + onglets hauts

- `.appbar` : collante en haut, logo degrade 36 px, nom du produit en gras,
  nom de l'entreprise en sous-titre, pastille `.now` avec la page courante.
- `.topnav` : rangee collante (`top: 52px`) de 10 pilules `.tab` de 36 px,
  defilable horizontalement (`overflow-x: auto`, scrollbar masquee) ;
  `.tab.on` passe en degrade bleu.
- Chaque pilule est un lien `<a href="..." target="_self">` vers l'`url_path`
  de la page : le changement d'ecran ne declenche aucun rerun de widget.
- `routes.executer()` appelle `st.navigation(sections, position="hidden")` puis
  `routes.barre_haut()`. Si la version de Streamlit ne connait pas `position`,
  le menu natif est laisse visible via `theme.montrer_sidebar()` ; sans
  `st.Page`, `executer_repli()` dessine la barre d'onglets + 5 boutons.

### 3. Filtres compacts (plus de colonne de filtres)

- Recherche en ligne pleine largeur, directement sous les onglets.
- Wilaya, metier, tri et bascule de disponibilite sont ranges dans un
  `st.expander` ("مرشحات · Filtres (n)") ouvert seulement si un filtre est pose.
- `cartes.puces_filtres()` resume les filtres actifs en puces `.fbar .chip`
  (un seul rendu HTML), pour garder le haut d'ecran lisible.

### 4. Cartes et actions

- `.karts` passe a une seule colonne (`grid-template-columns: 1fr`) a toutes
  les largeurs : on scrolle, on ne balaye pas.
- `.kart` : rayon 16 px, ombre douce, padding serre, avatar 38 px,
  etiquettes 10,5 px.
- `.acts` devient une pile verticale : chaque action (Appeler, WhatsApp,
  BaridiMob) est un bouton pleine largeur de 40 px, rayon 12 px, libelle
  aligne a gauche, arabe + francais visibles y compris sur telephone.
  WhatsApp en vert plein `#12B76A`, Appel en bleu clair, BaridiMob en ambre.

### 5. Widgets

Champs et boutons ramenes a 42 px (rayon 12 px), espacement vertical reduit
(`gap: .55rem`), `.hero` en rayon 20 px, `.kpi` en rayon 16 px, `st.tabs` en
pilules. Deux ruptures : `max-width: 640px` (telephone) et `min-width: 900px`
(cadre flottant).

Tout le CSS de cette version vit dans `ui/theme.py` (`CSS_V14`), injecte en
cinquieme couche par `theme.appliquer()`.
