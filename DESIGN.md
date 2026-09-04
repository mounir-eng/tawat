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
