# Site du Developers Group Dijon

Site statique de [developers-group-dijon.fr](https://developers-group-dijon.fr/), généré avec [Hugo](https://gohugo.io/). Les contenus sont écrits en [Asciidoc](https://docs.asciidoctor.org/asciidoc/latest/).

Le site ne contient aucune ligne de JavaScript, aucun cookie et aucun traceur. La charte graphique reprend celle du DevFest Dijon 2026.

## Publier du contenu

1. Créez une branche.
2. Ajoutez ou modifiez un fichier `.adoc` (voir ci-dessous).
3. Ouvrez une Pull Request vers `main`. La CI vérifie que le site se construit.
4. Une fois la PR mergée, le site est publié automatiquement sur le serveur SFTP.

### Nouvel article ou événement

```sh
hugo new content posts/2026-09-29-mon-evenement/index.adoc
```

Cette commande crée le dossier `content/posts/2026-09-29-mon-evenement/`, avec un `index.adoc` pré-rempli. Le nom du dossier commence par la date de création de l'article (`AAAA-MM-JJ-`) ; ce préfixe n'apparaît ni dans l'adresse ni dans le titre. Les images de l'article vont dans ce même dossier : `image::photo.webp[Description]`.

Dans l'en-tête du fichier (front matter) :

| Champ | Rôle |
|---|---|
| `title` | Titre de l'article |
| `date` | Date de publication |
| `slug` | Adresse de la page : `/slug/` |
| `categories` | `evenements` pour un événement, `news` pour une actualité (pas les deux) |
| `image` | Image de couverture (fichier du dossier), utilisée sur les cartes et les partages |
| `summary` | Résumé affiché sur les cartes |
| `evenement` | Bloc facultatif : `date`, `fin`, `horaire`, `lieu`, `inscription`, `prix`. Il affiche l'encadré « Infos pratiques » et classe l'événement dans « À venir » tant que sa date n'est pas passée. |
| `outputs: ["html", "calendar"]` | Génère en plus un fichier `.ics` « Ajouter à mon agenda » (à garder avec `evenement`). |

### Mémo Asciidoc

```asciidoc
== Titre de section
Paragraphe avec du *gras*, de l'_italique_ et un https://exemple.fr[lien].

* liste
* à puces

NOTE: Encadré (aussi TIP:, WARNING:, IMPORTANT:, CAUTION:).

image::photo.webp[Texte alternatif]

[source,kotlin]
----
fun main() = println("Bonjour Dijon")
----

link:https://my.weezevent.com/...[Je m'inscris !,role=button]
link:https://www.youtube.com/watch?v=...[Regarder la vidéo,role=video]
link:https://www.openstreetmap.org/search?query=...[Voir sur la carte,role=map]
```

Les vidéos et les cartes sont des liens, pas des iframes. On garde ainsi zéro JavaScript et aucun traceur tiers.

### Autres contenus

- **Bandeau DevFest de l'accueil** : section `[params.devfest]` de `hugo.toml`, à mettre à jour chaque année.
- **Partenaires** : `data/partenaires.yaml`, et les logos dans `static/images/partenaires/`.
- **Texte d'accueil** : `content/_index.adoc`.
- **Page « L'association »** (équipe, adhésion) : `content/association/index.adoc`.
- **Code de conduite** : `content/code-de-conduite/index.adoc`.
- **Menu** : `[menus]` dans `hugo.toml`.

## Travailler en local

Prérequis :
- [Hugo **extended**](https://gohugo.io/installation/) 0.151 ou plus ;
- Asciidoctor : `gem install asciidoctor rouge`.

```sh
hugo server          # http://localhost:1313, rechargement automatique
hugo --gc            # construit le site dans public/
```

## Publication automatique (GitHub Actions)

Le workflow `.github/workflows/site.yml` :

- **Sur chaque PR vers `main`** : construit le site et vérifie qu'aucun JavaScript n'est publié.
- **Sur chaque push dans `main`** (donc chaque merge) : construit le site, puis l'envoie sur le serveur SFTP avec `lftp mirror`.
- **À la demande** : bouton « Run workflow » dans l'onglet Actions.

### Configuration à faire une fois

Dans **Settings → Secrets and variables → Actions** du dépôt :

| Secret | Obligatoire | Contenu |
|---|---|---|
| `SFTP_HOST` | oui | Nom du serveur, par ex. `ftp.exemple.fr` |
| `SFTP_USER` | oui | Utilisateur SFTP |
| `SFTP_REMOTE_DIR` | oui | Dossier de destination sur le serveur, par ex. `/www` |
| `SFTP_PRIVATE_KEY` | l'un des deux | Clé privée SSH (recommandé) |
| `SFTP_PASSWORD` | l'un des deux | Mot de passe, si pas de clé |
| `SFTP_PORT` | non | Port, `22` par défaut |
| `SFTP_KNOWN_HOSTS` | recommandé | Empreinte du serveur : sortie de `ssh-keyscan -p 22 ftp.exemple.fr` |

La variable (onglet *Variables*, pas *Secrets*) `SFTP_DELETE` vaut `true` pour supprimer sur le serveur les fichiers qui ne font plus partie du site.

> ⚠️ **Avant d'activer `SFTP_DELETE`**, vérifiez que `SFTP_REMOTE_DIR` ne contient que le site. Tout le reste de ce dossier serait supprimé, y compris une ancienne installation WordPress.

Le job de publication utilise l'environnement GitHub `production`. Vous pouvez y ajouter une validation manuelle ou restreindre la publication à la branche `main` (**Settings → Environments**).

## Migration depuis WordPress

Tous les articles et pages de l'ancien site ont été convertis en Asciidoc. Leurs images ont été converties en WebP et placées dans le dossier de chaque article.

- **Adresses conservées** : `/mon-article/`, `/category/news/`, `/category/evenements/` et `/code-de-conduite/` restent identiques.
- **Article dont l'adresse contenait un emoji** : son ancienne adresse redirige vers la nouvelle.
- **Ancien flux RSS WordPress** : `/feed/` redirige vers `/index.xml`, via le `.htaccess`, uniquement si l'hébergement est sous Apache.
