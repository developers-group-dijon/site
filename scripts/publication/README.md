# Publication par issue : guide de maintenance

Ce dossier contient l'outillage qui transforme une issue « Annoncer un événement » ou « Publier une news » en Pull Request, avec ses visuels et son texte LinkedIn. Le mode d'emploi pour les membres est dans le [README](../../README.md#demander-une-publication-par-une-issue).

## Vue d'ensemble

```
Issue (formulaire)
  │
  ▼
gardien (publication-gardien.yml)          membre ? commande valide ?  → label publication:a-traiter
  │
  ▼
traitement (publication.yml) : traiter-issue.py, une étape par passage
  ├─ attente        → branche + PR en brouillon, 3 vignettes + texte de l'article
  │                   /visuel-site N + /texte-site ok
  ├─ site validé    → vignette enregistrée, 3 visuels LinkedIn + texte du post
  │                   /visuel-linkedin N + /texte-linkedin ok
  └─ linkedin validé → PR réécrite en 2 commits, prête à merger
```

## Principe

Chaque script fait une seule chose, prend ses paramètres en arguments (et un texte long sur l'entrée standard), et affiche son résultat. Ce qu'ils partagent est dans `commun/`, importé comme un module Python. `traiter-issue.py` n'est qu'un chef d'orchestre : il lance les autres scripts comme des commandes, que l'on peut aussi lancer un par un à la main.

Aucune dépendance Python hors de la bibliothèque standard.

### Le gardien

| Script | Rôle |
|---|---|
| `accueillir-issue.py ISSUE AUTEUR` | Nouvelle demande : membre → `publication:a-traiter` et liste des commandes ; sinon `publication:refusee`. Affiche `a-traiter` ou `refusee` |
| `verifier-commandes.py ISSUE AUTEUR COMMENTAIRE_ID < commentaire` | Commandes en commentaire : une commande valide pose `publication:a-traiter` et reçoit un 👍, une commande ignorée reçoit une explication. Affiche `a-traiter` si le label est posé |
| `creer-labels.py` | Crée ou met à jour les labels du dépôt |

### Le traitement

Dans l'ordre où `traiter-issue.py` les enchaîne :

| Script | Rôle |
|---|---|
| `traiter-issue.py [ISSUE…]` | Lit l'état de chaque issue et lance les scripts de l'étape suivante ; met à jour les labels |
| `etat-issue.py ISSUE` | Affiche en JSON l'état de l'issue, reconstruit à partir de ses labels et commentaires |
| `preparer-issue.py ISSUE` | Prépare `.publication/issue-N/` : copie de travail de la branche (ou de la base) et propositions en cours |
| `telecharger-images.py ISSUE DOSSIER` | Enregistre les images jointes à l'issue |
| `generer-propositions.py ISSUE ETAPE` | Lance Claude Code pour produire les propositions de l'étape (`site` ou `linkedin`) |
| `controler-propositions.py ETAPE DOSSIER` | Vérifie les fichiers produits et la sécurité des SVG, fait les rendus PNG |
| `publier-propositions.py ISSUE ETAPE` | Commite et pousse les propositions sur la branche, ouvre la PR au premier passage, commente l'issue |
| `enregistrer-vignette.py ISSUE` | Site validé : vignette WebP et date dans l'article |
| `finaliser-pr.py ISSUE` | LinkedIn validé : branche réécrite en deux commits, PR prête |
| `rendre-visuel.py SVG SORTIE` | Rend un SVG en PNG ou WebP avec les polices de la charte (utilisé aussi par Claude) |

### Modules communs et données

| Fichier | Rôle |
|---|---|
| `commun/github.py` | Appels à `gh`, mode essai |
| `commun/membres.py` | Lecture de `membres.txt` |
| `commun/etapes.py` | Labels et étape en cours |
| `commun/commandes.py` | Lecture et contrôle des commandes, texte d'aide |
| `commun/etat.py` | Reconstruction de l'état à partir des commentaires |
| `commun/depot.py` | Dossier de travail, copie git, push protégé |
| `commun/propositions.py` | Fichiers attendus d'une proposition, empreintes |
| `commun/article.py` | Champs du front matter |
| `commun/visuels.py` | Rendu et contrôle des SVG |
| `membres.txt` | Membres autorisés à publier (identifiants GitHub), lus sur `main` uniquement |
| `prompts/` | Consignes données à Claude pour le site et pour LinkedIn |
| `charte.md`, `exemples/` | Charte graphique des visuels et gabarits SVG commentés |
| `polices/`, `ressources/` | Polices du rendu et logos de l'association |
| `tests/` | Tests des modules communs |

Autour du dossier :

| Fichier | Rôle |
|---|---|
| `.github/ISSUE_TEMPLATE/evenement.yml`, `news.yml` | Formulaires d'issue, avec les labels `publication` et `type:…` |
| `.github/workflows/publication-gardien.yml` | Lance `accueillir-issue.py` à l'ouverture d'une issue de publication, `verifier-commandes.py` à chaque commentaire, puis le traitement si l'un d'eux affiche `a-traiter` |
| `.github/workflows/publication.yml` | Lance `traiter-issue.py` sur un runner ; relançable à la main depuis l'onglet Actions |
| `.github/CODEOWNERS` | Soumet à revue toute modification de ce dossier et de `.github/` |

## Labels et étapes

| Label | Posé par | Signification |
|---|---|---|
| `publication`, `type:evenement`, `type:news` | formulaire | Demande de publication et son type |
| `publication:a-traiter` | gardien | Une action attend le traitement (nouvelle demande ou commande valide) |
| `publication:refusee` | gardien | Demande d'une personne absente de `membres.txt` : issue ignorée |
| `publication:site` | traitement | PR en brouillon, propositions pour le site en attente de validation |
| `publication:linkedin` | traitement | Vignette et texte enregistrés, propositions LinkedIn en attente de validation |
| `publication:prete` | traitement | PR réécrite et prête à être relue et mergée |
| `publication:publiee` | après déploiement | Site publié, issue close |

Le gardien déduit l'étape en cours de ces labels (`commun/etapes.py`) : une commande `/…-site` n'est acceptée qu'à l'étape `site`, une commande `/…-linkedin` qu'à l'étape `linkedin`.

L'état détaillé (version des propositions, choix, consignes, branche) n'est stocké nulle part ailleurs que dans l'issue : `etat-issue.py` le reconstruit à chaque passage en relisant les commentaires. Les commentaires de propositions portent un marqueur invisible `<!-- publication {...} -->` avec les empreintes des fichiers proposés. Une validation reste acquise après une nouvelle version si l'élément validé n'a pas changé.

## La branche de la publication

Dès le premier passage, `publier-propositions.py` crée la branche `evenement/<issue>-<slug>` (ou `article/…` pour une news) et ouvre la PR en brouillon. Tout se passe dans le dossier de la publication :

```
content/posts/2026-10-18-mon-slug/
  index.adoc              texte proposé, puis validé (vignette provisoire : proposition 1)
  mon-slug.webp           vignette retenue (après /visuel-site N + /texte-site ok)
  propositions/
    site/                 proposition-1..3.svg/.png, meta.json
    linkedin/             carre-1..3.svg/.png, texte.txt, meta.json
    ressources/           logos
    entree/               images fournies dans l'issue
```

- Chaque version des propositions est un commit sur la branche ; les images des commentaires pointent sur ce commit, donc chaque commentaire garde ses propres images.
- Chaque push publie la branche sur le site de test (comportement du workflow Site) : on y voit l'article avec sa vignette, provisoire puis retenue.
- Hugo publie aussi les fichiers de `propositions/` avec la page, sans les utiliser : c'est sans conséquence et ils disparaissent à la finalisation.

**À la validation de LinkedIn**, `finaliser-pr.py` réécrit la branche à partir du `main` à jour, en deux commits : « Annonce : … » (`index.adoc` et la vignette WebP), puis « LinkedIn : visuel et texte du post » (`linkedin.png` et `linkedin.txt` dans le même dossier). Le dossier `propositions/` disparaît, la branche est poussée avec `--force-with-lease` et la PR passe en « prête ». Elle est alors fusionnable en fast-forward. Les images des anciennes propositions dans l'issue peuvent cesser de s'afficher après cette réécriture : elles ne servent plus.

## Ce que fait Claude, et ce qu'il ne fait pas

`generer-propositions.py` lance Claude Code dans la copie de travail (il y trouve `CLAUDE.md`, les règles de rédaction et la skill `article`) avec :

- les outils `Read`, `Glob`, `Grep`, `Write`, `Edit` et `Bash` seulement ;
- l'écriture autorisée **uniquement** dans le dossier de l'étape en cours, hors du dépôt ;
- `Bash` limité à `scripts/publication/rendre-visuel.py` (pour vérifier ses visuels) ;
- le mode `dontAsk` : tout le reste est refusé sans question ;
- ni accès web, ni `git`, ni `gh`, ni jeton GitHub dans son environnement.

Tout ce qui touche à git et à GitHub est fait par les scripts. Le contenu de l'issue est traité comme une donnée : les consignes demandent à Claude de signaler toute instruction qu'il y trouverait au lieu de la suivre. `controler-propositions.py` refuse en plus tout SVG qui contient un script, un `foreignObject`, un gestionnaire d'événement ou une URL distante.

Le merge reste manuel : la PR passe par la revue et la CI habituelles.

## Exécution dans GitHub Actions

Quand le gardien pose `publication:a-traiter`, son job `traiter` appelle `publication.yml`, qui lance `traiter-issue.py <issue>` sur un runner. Les propositions arrivent donc quelques minutes après chaque demande ou commande, sans PC allumé.

Le traitement s'authentifie de deux façons :

- **Claude Code** avec un token d'abonnement (`CLAUDE_CODE_OAUTH_TOKEN`) : l'usage est décompté sur l'abonnement de la personne qui a généré le token.
- **GitHub** avec le jeton d'une GitHub App de l'association, créé à chaque exécution. Contrairement au jeton du workflow, ses push et sa Pull Request déclenchent la CI (workflow Site). La branche, la PR et les commentaires apparaissent au nom du bot de l'application, reconnu grâce à la variable `PUBLICATION_BOT`.

Une exécution par issue à la fois : un traitement en attente peut être remplacé par un plus récent, sans perte, puisque chaque passage relit tout l'état de l'issue. En cas d'échec, le traitement le signale dans l'issue avec le lien du journal ; les journaux de Claude sont conservés 7 jours en artefact du run. Pour relancer : onglet **Actions → Publication — traitement → Run workflow**, avec le numéro de l'issue (ou vide pour toutes les issues `publication:a-traiter`).

## Configuration, une seule fois

1. Créer les labels, depuis un poste connecté à GitHub avec `gh auth login` : `scripts/publication/creer-labels.py`.
2. Dans **Settings → Branches** (règle de `main`), activer « Require review from Code Owners ».
3. **Créer la GitHub App** (Settings de l'organisation ou du compte → Developer settings → GitHub Apps → New GitHub App) :
   - nom au choix, par exemple « DGD Publication » ; c'est lui qui apparaîtra comme auteur ;
   - *Webhook* : décocher « Active » ;
   - *Repository permissions* : **Contents**, **Issues** et **Pull requests** en lecture et écriture, rien d'autre ;
   - *Where can this GitHub App be installed?* : « Only on this account ».
4. Dans la page de l'application : noter le **Client ID**, puis **Generate a private key** (un fichier `.pem` est téléchargé).
5. **Installer l'application** (Install App) sur le seul dépôt `site`.
6. **Générer le token Claude** sur un poste où Claude Code est connecté avec l'abonnement à utiliser : `claude setup-token`. Le token est valable un an ; noter sa date d'expiration.
7. Dans le dépôt, **Settings → Environments → New environment** `publication` :
   - *Deployment branches and tags* : « Selected branches », uniquement `main` ;
   - *Environment secrets* : `PUBLICATION_APP_PRIVATE_KEY` (contenu du `.pem`) et `CLAUDE_CODE_OAUTH_TOKEN` (le token de l'étape 6) ;
   - *Environment variables* : `PUBLICATION_APP_CLIENT_ID` (Client ID de l'étape 4) et, facultatif, `PUBLICATION_MODELE` (`sonnet` par défaut dans Actions).

**Renouvellement** : régénérer le token Claude avant son expiration et mettre à jour le secret. La clé privée de l'application n'expire pas ; la régénérer si elle a pu fuiter.

## Lancer à la main

Utile pour tester une modification avant le merge, ou si Actions n'est pas configuré. Prérequis :

- **Python 3.10+**, **git** et la **[GitHub CLI](https://cli.github.com/)** connectée avec un compte présent dans `membres.txt` (`gh auth login`) : ses commentaires et sa PR sont alors à son nom ;
- **[Claude Code](https://code.claude.com/)** connecté (`claude auth login`) : l'abonnement de la personne qui lance le script est utilisé ;
- **[resvg](https://github.com/linebender/resvg/releases)** et **cwebp** (paquet `webp`) ou ImageMagick ;
- facultatif : **Hugo** et **Asciidoctor**, pour construire le site avant la finalisation (sinon la CI s'en charge).

```sh
scripts/publication/traiter-issue.py          # toutes les issues « publication:a-traiter »
scripts/publication/traiter-issue.py 42       # seulement l'issue 42
scripts/publication/etat-issue.py 42          # où en est l'issue 42
```

Chaque passage fait avancer chaque issue d'**une** étape puis s'arrête, et peut être relancé sans risque. Compter quelques minutes par issue quand Claude travaille. Les scripts de l'étape peuvent aussi être lancés un par un, dans l'ordre du tableau ci-dessus.

| Variable | Défaut | Rôle |
|---|---|---|
| `PUBLICATION_MODELE` | `opus` (`sonnet` dans Actions) | Modèle utilisé par Claude Code |
| `PUBLICATION_MAX_TOURS` | `80` | Nombre maximal d'étapes de Claude par proposition |
| `PUBLICATION_BASE` | `origin/main` | Base des branches de publication ; `origin/<branche>` pour essayer l'outillage avant son merge |
| `PUBLICATION_ESSAI` | | `1` : affiche les écritures sur GitHub (labels, commentaires, PR, push) au lieu de les faire |
| `PUBLICATION_BOT` | | Identifiant du bot de la GitHub App, défini dans Actions |

Le dossier `.publication/` (ignoré par git) contient les copies de travail, le dossier de travail de Claude et le journal de chaque appel (`claude-issue-N-etape-vV.log`). Il peut être supprimé à tout moment : tout ce qui compte est sur GitHub.

## Visuels

- Vignette du site : SVG 1600 × 900 rendu en WebP dans le dossier de l'article (`image:` du front matter).
- Carré LinkedIn : SVG 1200 × 1200 rendu en PNG (`linkedin.png`), avec le texte du post (`linkedin.txt`), dans le dossier de l'article.
- Polices : instances statiques des polices du site (`static/fonts/`) au format TTF, lisible par resvg. Bitcount Grid Single est figée sur l'axe `ELSH` 50 (pixels carrés, comme sur le site) en graisses 400, 500 et 700. Licence SIL Open Font License 1.1.
- Pour faire évoluer le style, modifier `charte.md` et les gabarits de `exemples/` : Claude les lit à chaque proposition.

```sh
scripts/publication/rendre-visuel.py scripts/publication/exemples/vignette.svg /tmp/vignette.png
```

## Essayer et tester

Les tests des modules communs, sans réseau :

```sh
python3 -m unittest discover -s scripts/publication
```

Pour essayer un script du gardien sur une vraie issue sans la modifier :

```sh
PUBLICATION_ESSAI=1 scripts/publication/accueillir-issue.py 42 mon-login
printf '/visuel-site 2\n/texte-site ok\n' | PUBLICATION_ESSAI=1 scripts/publication/verifier-commandes.py 42 mon-login 123456
```

## En cas de problème

- **« n'est pas dans membres.txt »** : le compte `gh` qui lance `traiter-issue.py` doit figurer dans la liste.
- **Claude a échoué** : lire le journal (`.publication/claude-issue-N-<etape>-v<version>.log` en local, artefact du run dans Actions), puis relancer. Les labels ne sont retirés qu'en cas de succès.
- **Le traitement ne démarre pas dans Actions** : vérifier l'environnement `publication` (secrets, variable `PUBLICATION_APP_CLIENT_ID`, branche `main` autorisée) et l'installation de la GitHub App sur le dépôt. Un échec de `claude` à l'authentification signale en général un token expiré.
- **Push refusé (« stale info »)** : quelqu'un a poussé sur la branche de la publication pendant le traitement. Relancer : il repart de la version distante.
- **Retouche à la main pendant le brouillon** : possible sur la branche, mais une nouvelle version des propositions du site remplace `index.adoc`, et la finalisation ne garde que `index.adoc`, la vignette WebP et les deux fichiers LinkedIn. Le plus sûr est de retoucher après le passage en « prête ».
- **Recommencer une étape** : dans l'issue, `/modifier-site …` ou `/modifier-linkedin …` avec une consigne.

## Ajouter un script

- Un fichier exécutable `verbe-objet.py` dans ce dossier, avec une docstring qui commence par ce qu'il fait et son usage (affichée en cas d'arguments incorrects).
- Arguments simples en ligne de commande, texte long sur l'entrée standard, résultat sur la sortie standard, messages de diagnostic sur la sortie d'erreur.
- Tout ce qui sert à plus d'un script va dans `commun/`, avec un test dans `tests/`.
