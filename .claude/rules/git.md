# Règles git

## Ce que Claude peut faire

- Créer des branches, faire des commits, rebaser ses propres branches locales.
- Lire l'état du dépôt distant : `git fetch`, `git log origin/main`, etc.

## Ce que Claude ne fait jamais

- **Aucun `git push`**, sous aucune forme (y compris `--force`, `-u`, vers une autre remote). Le push est une opération manuelle. À la fin du travail, indiquer à l'utilisateur ou l'utilisatrice la commande à lancer, par exemple `git push -u origin <branche>`.
- **Aucun commit sur `main`.** Tout commit se fait sur une branche dédiée au sujet traité.
- Pas de merge dans `main` : l'intégration se fait par Pull Request sur GitHub.

Un hook (`.claude/hooks/garde-git.sh`) et une règle de permission (`.claude/settings.json`) bloquent le push et le commit sur `main`. Ces blocages sont un filet de sécurité : la règle s'applique même dans un cas qu'ils ne détecteraient pas.

## Branches

- Créer la branche **avant** de modifier des fichiers, à partir de `main` à jour :

  ```sh
  git fetch origin
  git switch --no-track -c <type>/<sujet> origin/main
  ```

  `--no-track` est indispensable : sans lui, la branche suit `origin/main` et un `git push` sans argument viserait `main`.
- Si le travail dépend d'une branche pas encore mergée (par exemple une correction qui a besoin des fichiers d'une autre branche), partir de cette branche et le signaler : les deux branches devront être mergées dans l'ordre.
- Nom en minuscules et tirets, préfixé par le type : `article/`, `evenement/`, `fix/`, `feat/`, `docs/`, `chore/`. Exemples : `article/devfest-2026-programme`, `fix/menu-mobile`.
- Une branche par sujet. Ne pas mélanger un article et une modification de gabarit.
- Commande à part : `git switch -c …` dans un appel, `git commit` dans un autre (le hook vérifie la branche courante avant l'exécution de la commande).
- Le hook détecte `git push` en début de ligne, même dans un heredoc : écrire les messages de commit dans un fichier (`git commit -F fichier`) plutôt qu'en heredoc s'ils contiennent une telle ligne.

## Merge fast-forward uniquement : rebaser

Les merges vers `main` sont en **fast-forward only**. Une branche doit donc toujours partir du dernier commit de `origin/main`.

Au début de toute session qui reprend une branche existante (travail commencé lors d'un échange précédent), et avant de rendre la main :

```sh
git fetch origin
git rebase origin/main
```

- Si `git rebase` signale des conflits : les résoudre en conservant les deux intentions, puis `git rebase --continue`. En cas de doute sur la bonne résolution, `git rebase --abort` et demander.
- Après un rebase d'une branche déjà poussée, le push devra être forcé : le signaler et proposer `git push --force-with-lease`, sans le lancer.
- Pas de commit de merge (`git merge origin/main`) dans une branche : toujours rebaser.
- Vérifier après le rebase que le site se construit et que `scripts/verifier-site.sh` passe.

## Commits

- Messages en français, à l'impératif ou au présent, courts et descriptifs, comme l'historique existant (« Publication en SFTP avec suppression des fichiers obsolètes »).
- Un commit par étape cohérente ; ne jamais commiter `public/`, `resources/` ni des fichiers temporaires.
