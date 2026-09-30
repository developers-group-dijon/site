# Règles de développement

Tout développement du site (gabarits `layouts/`, CSS `assets/css/`, fichiers `static/`, `hugo.toml`, `archetypes/`, contenus Asciidoc) respecte ces règles. Si une demande ne peut pas être réalisée sans en enfreindre une, ne pas la contourner : l'expliquer et proposer une alternative conforme.

## 1. Site statique Hugo

- Le site est entièrement généré par Hugo au build. Pas de code serveur, pas d'API appelée depuis le navigateur, pas de formulaire traité par le site (les inscriptions passent par un lien vers un service externe, par exemple Weezevent).
- Pas de thème ni de module Hugo externe : les gabarits vivent dans `layouts/`.
- Les ressources CSS passent par les Hugo Pipes (`resources.Get` → `minify` → `fingerprint`), comme dans `layouts/baseof.html`.
- Tout fichier servi est dans le dépôt : polices dans `static/fonts/`, images dans le dossier de l'article ou dans `static/images/`. Aucun CDN, aucune police Google Fonts, aucune ressource chargée depuis un autre domaine.
- Le site doit se construire sans erreur ni avertissement avec la version de Hugo de la CI (`.github/workflows/site.yml`).

## 2. Zéro JavaScript

Le site ne contient aucune ligne de JavaScript, aucun cookie et aucun traceur. Sont donc interdits, dans les gabarits comme dans les contenus :

- les balises `<script>` (y compris JSON-LD, analytics, widgets) et les fichiers `.js` ;
- les attributs de gestion d'événements (`onclick`, `onload`, `onerror`…) et les URL `javascript:` ;
- les `<iframe>` et intégrations tierces (YouTube, cartes, formulaires, réseaux sociaux) : on met un lien à la place, avec `role=video`, `role=map` ou `role=button` ;
- les blocs de passage brut Asciidoc (`++++`, `pass:[]`) qui injecteraient l'un des éléments ci-dessus.

Les comportements interactifs se font en HTML et CSS : `<details>`/`<summary>`, `:target`, `:hover`, `:focus-visible`, ancres, etc. Si un besoin semble exiger du JavaScript, le signaler au lieu de l'ajouter.

`scripts/verifier-site.sh` contrôle ces interdits sur le site construit ; la CI l'exécute à chaque build.

## 3. Desktop et mobile

Chaque page doit être lisible et utilisable de 320 px à 1920 px de large.

- Garder la balise `<meta name="viewport" content="width=device-width, initial-scale=1">` de `baseof.html`.
- Conception fluide : largeurs en `%`, `fr`, `minmax()`, `clamp()` ; pas de largeur fixe en pixels sur un conteneur. Réutiliser les variables `--largeur` et `--marge` de `main.css`.
- Aucun défilement horizontal de la page. Seuls les blocs de code et les tableaux peuvent défiler horizontalement, dans leur propre conteneur (`overflow-x: auto`).
- Les images ont `max-width: 100%` et `height: auto` ; ajouter `loading="lazy"` et `decoding="async"` hors de la première vue.
- Les zones cliquables (liens de menu, boutons) font au moins 44 × 44 px sur mobile.
- Les règles `@media` restent dans `assets/css/main.css`, avec les points de rupture existants (600, 700, 900 et 1000 px) plutôt que de nouveaux.
- Respecter `prefers-reduced-motion` pour toute animation ou transition.
- Avant de conclure une modification visuelle, vérifier le rendu avec `hugo server` à 360 px et à 1280 px de large au minimum.

## 4. Accessibilité et sobriété

- HTML sémantique : `<header>`, `<nav>`, `<main>`, `<article>`, `<footer>`, un seul `<h1>` par page, niveaux de titres sans saut.
- Chaque image porteuse de sens a un texte alternatif ; une image décorative a `alt=""`.
- Contraste suffisant (WCAG AA) avec les couleurs de la charte définies dans `:root`.
- Le focus clavier reste visible (`:focus-visible`) et le lien d'évitement « Aller au contenu » est conservé.
- Images en WebP, redimensionnées à la taille d'affichage utile.
