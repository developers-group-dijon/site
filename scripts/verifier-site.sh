#!/usr/bin/env bash
# Vérifie les garde-fous du site sur le dossier généré par Hugo :
# zéro JavaScript, pas d'iframe, balise viewport présente sur chaque page.
# Usage : scripts/verifier-site.sh [dossier]   (par défaut : public)
set -uo pipefail

dossier="${1:-public}"
if [ ! -d "$dossier" ]; then
  echo "Dossier « $dossier » introuvable : lancez d'abord « hugo build »." >&2
  exit 2
fi

erreurs=0
echec() {
  echo "::error::$1"
  shift
  printf '  %s\n' "$@"
  erreurs=$((erreurs + 1))
}

# Fichiers JavaScript
mapfile -t fichiers < <(find "$dossier" -type f \( -name '*.js' -o -name '*.mjs' \))
[ ${#fichiers[@]} -eq 0 ] || echec "Fichiers JavaScript interdits :" "${fichiers[@]}"

# Motifs interdits dans le HTML
verifier() {
  local message="$1" motif="$2" resultat
  resultat=$(grep -rilE --include='*.html' "$motif" "$dossier")
  [ -z "$resultat" ] || echec "$message" $resultat
}
verifier "Balise <script> interdite :" '<script'
verifier "Attribut d'événement JavaScript (onclick, onload…) interdit :" '<[^>]+[[:space:]]on[a-z]+[[:space:]]*='
verifier "URL javascript: interdite :" '(href|src|action)=["'"'"']?[[:space:]]*javascript:'
verifier "Balise <iframe> interdite (mettre un lien) :" '<iframe'

# Balise viewport sur chaque page (hors pages de redirection des alias Hugo)
mapfile -t sans_viewport < <(grep -rlE --include='*.html' '<html' "$dossier" \
  | xargs -r -d '\n' grep -LiE 'http-equiv="?refresh' \
  | xargs -r -d '\n' grep -LE '<meta[^>]+name="?viewport')
[ ${#sans_viewport[@]} -eq 0 ] || echec "Pages sans balise meta viewport (affichage mobile) :" "${sans_viewport[@]}"

if [ "$erreurs" -gt 0 ]; then
  echo "$erreurs contrôle(s) en échec."
  exit 1
fi
echo "Garde-fous respectés : aucun JavaScript, aucune iframe, viewport présent partout."
