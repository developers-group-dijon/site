---
name: article
description: Rédiger, relire ou modifier un article ou un événement du site du Developers Group Dijon (content/posts/). À utiliser dès qu'on demande d'écrire un post, une news, une annonce d'événement, un compte rendu, ou de relire un texte du site.
---

# Rédiger un article

Les règles de `.claude/rules/redaction.md` (liens vers les partenaires, écriture inclusive) et de `.claude/rules/code.md` (zéro JavaScript) s'appliquent. Cette skill décrit le déroulé et la vérification finale.

## 1. Rassembler les informations

Avant d'écrire, s'assurer d'avoir :

- le type : événement (`categories: ["evenements"]`) ou actualité (`categories: ["news"]`) ;
- pour un événement : date et heure de début et de fin, lieu avec adresse, lien d'inscription, prix ;
- les partenaires, sponsors et lieux d'accueil à citer, avec leur site ;
- les images fournies (à convertir en WebP si besoin) et l'auteur ou l'autrice.

Ne rien inventer : une date, une adresse, une URL ou un nom manquant se demande.

## 2. Créer l'article

```sh
hugo new content posts/AAAA-MM-JJ-sujet-court/index.adoc
```

`AAAA-MM-JJ` est la date du jour. Compléter le front matter généré (voir le README) : `title`, `slug`, `categories`, `auteur`, `summary`, `image`, et pour un événement le bloc `evenement` avec `outputs: ["html", "calendar"]`. Pour une news, supprimer le bloc `evenement` et la ligne `outputs`.

## 3. Rédiger

- Un premier paragraphe qui dit l'essentiel : quoi, quand, où, pour qui.
- Des sections `==` courtes, des listes pour les programmes.
- Les appels à l'action en boutons : `link:URL[Je m'inscris !,role=button]`.
- Vidéos et cartes en liens (`role=video`, `role=map`), jamais en iframe.
- Le `summary` fait une ou deux phrases, sans point médian.
- Ton : chaleureux et direct, en vouvoyant le public. Emojis avec modération.

## 4. Vérifier avant de rendre la main

Relire le texte entier et cocher chaque point :

- [ ] **Partenaires** : lister toutes les organisations citées (y compris le lieu d'accueil). Comparer avec `data/partenaires.yaml`. Chacune a au moins une mention en lien, avec l'URL du fichier ou son site officiel vérifié.
- [ ] **Double forme** : chercher les noms de personnes au masculin pluriel (développeurs, participants, inscrits, speakers invités, étudiants, tous, ceux…) et les remplacer par une double forme ou un terme épicène.
- [ ] **Point médian** : `grep -n '·' index.adoc`. Chaque occurrence est dans un titre ou un bouton ; sinon, la réécrire en double forme.
- [ ] **Liens** : toutes les URL sont complètes, en `https://`, et aucune n'est inventée.
- [ ] **Images** : chaque `image::` a un texte alternatif, les fichiers sont dans le dossier de l'article.
- [ ] **Build** : `hugo build --minify && scripts/verifier-site.sh public` passe sans erreur.

Dans le message final, indiquer les partenaires liés et toute information restée à confirmer.
