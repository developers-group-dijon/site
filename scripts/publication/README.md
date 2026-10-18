# Publication par issue : guide de maintenance

Ce dossier contient l'outillage qui suit une demande de publication, depuis une issue « Annoncer un événement » ou « Publier une news ». Le mode d'emploi pour les membres est dans le [README](../../README.md#demander-une-publication-par-une-issue).

## Principe

Chaque script fait une seule chose, prend ses paramètres en arguments (et un texte long sur l'entrée standard), et affiche son résultat. Ce qu'ils partagent est dans `commun/`, importé comme un module Python. Aucune dépendance hors de la bibliothèque standard : seuls `python3` (3.10 ou plus) et la [GitHub CLI](https://cli.github.com/) (`gh`) sont nécessaires.

| Fichier | Rôle |
|---|---|
| `membres.txt` | Membres autorisés à publier (identifiants GitHub), lus sur `main` uniquement |
| `accueillir-issue.py ISSUE AUTEUR` | Nouvelle demande : membre → `publication:a-traiter` et liste des commandes ; sinon `publication:refusee` |
| `verifier-commandes.py ISSUE AUTEUR COMMENTAIRE_ID < commentaire` | Commandes en commentaire : une commande valide pose `publication:a-traiter` et reçoit un 👍, une commande ignorée reçoit une explication |
| `creer-labels.py` | Crée ou met à jour les labels du dépôt |
| `commun/github.py` | Appels à `gh` (labels, commentaires, réactions), mode essai |
| `commun/membres.py` | Lecture de `membres.txt` |
| `commun/etapes.py` | Labels et étape en cours d'une demande |
| `commun/commandes.py` | Lecture et contrôle des commandes, texte d'aide |
| `tests/` | Tests des modules communs |

Autour du dossier :

| Fichier | Rôle |
|---|---|
| `.github/ISSUE_TEMPLATE/evenement.yml`, `news.yml` | Formulaires d'issue, avec les labels `publication` et `type:…` |
| `.github/workflows/publication-gardien.yml` | Lance `accueillir-issue.py` à l'ouverture d'une issue de publication, `verifier-commandes.py` à chaque commentaire |
| `.github/CODEOWNERS` | Soumet à revue toute modification de ce dossier et de `.github/` (workflows, formulaires d'issue) |

## Labels et étapes

| Label | Posé par | Signification |
|---|---|---|
| `publication`, `type:evenement`, `type:news` | formulaire | Demande de publication et son type |
| `publication:a-traiter` | gardien | Une action attend le traitement (nouvelle demande ou commande valide) |
| `publication:refusee` | gardien | Demande d'une personne absente de `membres.txt` : issue ignorée |
| `publication:site` | traitement | Propositions pour le site en attente de validation |
| `publication:linkedin` | traitement | Propositions LinkedIn en attente de validation |
| `publication:prete` | traitement | Pull Request prête à être relue et mergée |
| `publication:publiee` | traitement | Site déployé, issue close |

Le gardien déduit l'étape en cours de ces labels (`commun/etapes.py`) : une commande `/…-site` n'est acceptée qu'à l'étape `site`, une commande `/…-linkedin` qu'à l'étape `linkedin`. Tant que les propositions ne sont pas publiées (étape `attente`), toutes les commandes sont refusées avec une explication.

Le gardien n'appelle aucune IA et ne touche pas au code : il ne pose que des labels et répond en commentaire.

## Sécurité

- Le workflow lit les scripts et `membres.txt` sur la branche par défaut, jamais sur une branche proposée.
- Le titre, le corps et les commentaires d'une issue ne sont jamais interpolés dans une commande : ils passent par des variables d'environnement, et le commentaire par l'entrée standard.
- Les commentaires des bots sont ignorés.
- Le jeton du workflow n'a que les droits `contents: read` et `issues: write`.

## Configuration, une seule fois

1. Créer les labels, depuis un poste connecté à GitHub avec `gh auth login` : `scripts/publication/creer-labels.py`.
2. Dans **Settings → Branches** (règle de `main`), activer « Require review from Code Owners » : `membres.txt`, les workflows et les formulaires ne changent alors qu'après revue.

## Essayer et tester

Les tests des modules communs, sans réseau :

```sh
python3 -m unittest discover -s scripts/publication
```

Pour essayer un script sur une vraie issue sans la modifier, `PUBLICATION_ESSAI=1` affiche les opérations d'écriture au lieu de les faire (les lectures, elles, interrogent GitHub) :

```sh
PUBLICATION_ESSAI=1 scripts/publication/accueillir-issue.py 42 mon-login
printf '/visuel-site 2\n/texte-site ok\n' | PUBLICATION_ESSAI=1 scripts/publication/verifier-commandes.py 42 mon-login 123456
```

## Ajouter un script

- Un fichier exécutable `verbe-objet.py` dans ce dossier, avec une docstring qui commence par ce qu'il fait et son usage (affichée en cas d'arguments incorrects).
- Arguments simples en ligne de commande, texte long sur l'entrée standard, résultat sur la sortie standard, messages de diagnostic sur la sortie d'erreur.
- Tout ce qui sert à plus d'un script va dans `commun/`, avec un test dans `tests/`.
