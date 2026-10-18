# Charte des visuels de publication

Les visuels reprennent l'identité du DevFest Dijon 2026, celle du site (`assets/css/main.css`) : pixel art, trames en damier, ombres décalées, contrastes francs. Exemple de référence : la vignette de `content/posts/2026-09-29-tremplin-devfest-2026/`.

## Formats

| Visuel | Taille | Usage |
|---|---|---|
| Vignette du site | 1600 × 900 (16:9) | Carte de l'article (recadrée en 16:9, affichée à environ 360 px de large) et image de partage |
| Carré LinkedIn | 1200 × 1200 | Post LinkedIn, lu surtout sur mobile |

Gabarits commentés : `exemples/vignette.svg` et `exemples/carre.svg`.

## Couleurs

| Nom | Valeur | Usage |
|---|---|---|
| noir | `#212121` | Fond sombre, texte sur jaune |
| rose | `#c2456a` | Titre, aplats |
| rose foncé | `#9a1a41` | Aplats, dégradé en escalier (`#9a1a41` → `#a8284f` → `#b3345b` → `#c2456a`) |
| rose clair | `#ffb7c1` | Accents |
| rose pâle | `#fff5f7` | Fond clair |
| jaune | `#ffd93d` | Surtitre, bandeau date et lieu, accent |
| blanc | `#ffffff` | Texte sur fond sombre |
| gris | `#717171` | Texte secondaire sur fond clair |

Toujours un contraste suffisant : texte blanc ou jaune sur noir ou rose foncé, texte noir sur jaune ou rose pâle. Pas de texte rose sur rose.

## Typographie

Seules ces polices existent au rendu (`polices/`) ; toute autre police est remplacée par Noto Sans.

- **Bitcount Grid Single** (pixel), graisses `500` et `700` : surtitre, titre, bandeau date et lieu. En capitales pour le surtitre et le bandeau.
- **Noto Sans**, graisses `300`, `400`, `600` et `700` : phrases d'accroche, noms des intervenantes et intervenants.

Tailles indicatives pour la vignette 1600 × 900 : titre 100 à 130 px, accroche 34 à 40 px, surtitre et bandeau 32 à 40 px. Rien en dessous de 30 px : la vignette est réduite à environ 360 px de large sur mobile. Pour le carré 1200 × 1200, 10 % plus grand.

Le moteur de rendu ne fait **pas de retour à la ligne automatique** : couper soi-même les lignes avec des `<tspan>` et vérifier sur le rendu que rien ne déborde.

## Motifs

- **Trame** : damier de 6 px en noir à 15 % d'opacité, posé sur un aplat (motif `trame` des exemples).
- **Escaliers et blocs de pixels** : rectangles alignés sur une grille de 20, 40 ou 80 px, avec `shape-rendering="crispEdges"`.
- **Ombre décalée** : copie noire de la forme, décalée de 6 à 12 px vers le bas à droite (comme les cartes du site).
- **Pictogrammes** en pixel art dessinés avec des rectangles (micro, écran, accolades, ampoule…), jamais de clipart.

## Composition

- Marges d'au moins 80 px ; rien d'important dans les 80 px du bord (recadrages).
- Une hiérarchie claire : surtitre (format : MEETUP, ATELIER, NEWS…) → titre → accroche → bandeau date · heure · lieu.
- Le logo de l'association (`ressources/logo-dgd-blanc.png`, blanc, ratio 979 × 426) sur fond sombre, en petit. Le logo DevFest (`ressources/logo-devfest.png`) uniquement pour un événement DevFest.
- Pour une news : pas de bandeau date, un surtitre « NEWS » ou la thématique.
- Les images fournies dans l'issue (photos, logos de partenaires) sont dans `entree/` : les intégrer quand elles servent le visuel (photo d'intervenant dans un cadre pixel, logo du lieu d'accueil sur un cartouche blanc).

## Contraintes techniques du SVG

- `width`, `height` et `viewBox` fixés au format exact.
- Images liées en chemin relatif au fichier SVG : `../ressources/…`, `../entree/…`. Pas d'URL distante, pas d'image encodée en base64 de plus de quelques kilo-octets.
- Pas de `<script>`, pas de `<foreignObject>`, pas de filtre CSS : uniquement des formes, du texte, des motifs (`<pattern>`), des dégradés et des images.
- Les caractères `&`, `<` et `>` dans le texte s'écrivent `&amp;`, `&lt;` et `&gt;`.
