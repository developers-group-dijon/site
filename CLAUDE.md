# Site du Developers Group Dijon

Site statique [Hugo](https://gohugo.io/), contenus en Asciidoc, publié en SFTP par GitHub Actions. Le [README](README.md) décrit l'arborescence, le front matter des articles et la publication.

## Règles à respecter

Ces fichiers sont chargés automatiquement par Claude Code. Ils s'appliquent à tout développement et à tout contenu, y compris quand la demande ne les mentionne pas :

- [.claude/rules/code.md](.claude/rules/code.md) : développement (Hugo statique, **zéro JavaScript**, compatibilité desktop et mobile).
- [.claude/rules/redaction.md](.claude/rules/redaction.md) : rédaction (lien vers chaque partenaire cité, écriture inclusive par la double forme).
- [.claude/rules/git.md](.claude/rules/git.md) : git (**jamais de push**, jamais de commit sur `main`, rebase sur `origin/main` car les merges sont en fast-forward only).

Pour rédiger ou modifier un article, utiliser la skill `article` (`.claude/skills/article/`).

## Commandes

```sh
hugo server                          # aperçu sur http://localhost:1313
hugo build --minify                  # construit le site dans public/
scripts/verifier-site.sh public      # contrôle les garde-fous sur le site construit
hugo new content posts/AAAA-MM-JJ-mon-sujet/index.adoc   # nouvel article
```

Après toute modification, construire le site et lancer `scripts/verifier-site.sh` : la CI exécute le même contrôle et bloque la publication en cas d'échec.
