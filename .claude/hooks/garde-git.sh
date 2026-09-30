#!/usr/bin/env bash
# Hook PreToolUse (Bash) : applique les règles git de .claude/rules/git.md.
# - refuse tout « git push » (le push est une opération manuelle) ;
# - refuse « git commit » quand la branche courante est main.
entree=$(cat)
commande=$(jq -r '.tool_input.command // ""' <<<"$entree")
dossier=$(jq -r '.cwd // "."' <<<"$entree")

refuser() {
  jq -n --arg raison "$1" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $raison}}'
  exit 0
}

# « git » en début de commande (ou après ; && || | ( ), suivi de ses seules
# options globales (-C dossier, -c clé=valeur, --option), puis de la sous-commande.
# Le texte d'un message de commit ou d'un heredoc n'est donc pas pris en compte.
sous_commande() {
  grep -qE "(^|[;&|(]|\\$\()[[:space:]]*git(([[:space:]]+-[Cc][[:space:]]+[^[:space:]]+)|([[:space:]]+--?[^[:space:]]+))*[[:space:]]+$1([[:space:]]|\$|[;&|)])" <<<"$commande"
}

if sous_commande push; then
  refuser "git push est interdit à Claude : le push est une opération manuelle (voir .claude/rules/git.md). Indiquer à l'utilisateur la commande à lancer."
fi

if sous_commande commit; then
  branche=$(git -C "$dossier" branch --show-current 2>/dev/null)
  if [ "$branche" = "main" ]; then
    refuser "Commit interdit sur main (voir .claude/rules/git.md). Créer d'abord une branche dédiée dans une commande séparée : git switch -c <type>/<sujet>."
  fi
fi

exit 0
