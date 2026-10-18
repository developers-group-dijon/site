#!/usr/bin/env python3
"""Fait avancer des issues de publication d'une étape, en enchaînant les scripts.

Usage : traiter-issue.py [ISSUE…]

Sans numéro : toutes les issues ouvertes avec le label « publication:a-traiter ».
Pour chaque issue, lit son état (etat-issue.py), puis selon l'étape :

  attente                     preparer-issue, telecharger-images,
                              propositions du site                    → publication:site
  site, /modifier-site …      preparer-issue, propositions du site
  site validé                 preparer-issue, enregistrer-vignette,
                              propositions LinkedIn                   → publication:linkedin
  linkedin, /modifier-…       preparer-issue, propositions LinkedIn
  linkedin validé             preparer-issue, finaliser-pr            → publication:prete

« Propositions » enchaîne generer-propositions, controler-propositions et
publier-propositions. Le label « publication:a-traiter » n'est retiré qu'en
cas de succès : en cas d'échec, relancer suffit, chaque passage repart de
l'état de l'issue.

Prérequis : git, gh, claude, resvg et cwebp (ou ImageMagick). Hors de GitHub
Actions (PUBLICATION_BOT vide), le compte gh doit figurer dans membres.txt,
sinon ses commentaires de propositions ne seraient pas reconnus.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from commun import depot, etapes, etat, github, membres, visuels

ICI = Path(__file__).resolve().parent


class Echec(Exception):
    pass


def lancer(script: str, *args) -> str:
    """Lance un script de ce dossier ; sa sortie d'erreur reste affichée."""
    res = subprocess.run([sys.executable, str(ICI / script), *map(str, args)], text=True, stdout=subprocess.PIPE)
    if res.returncode != 0:
        raise Echec(f"{script} a échoué")
    return res.stdout.strip()


def proposer(issue: int, etape: str) -> None:
    lancer("generer-propositions.py", issue, etape)
    lancer("controler-propositions.py", etape, depot.propositions(issue) / etape)
    lancer("publier-propositions.py", issue, etape)


def changer_etape(issue: int, ancienne: str | None, nouvelle: str) -> None:
    github.ajouter_label(issue, f"publication:{nouvelle}")
    if ancienne:
        github.retirer_label(issue, f"publication:{ancienne}")


def traiter(numero: int) -> None:
    e = json.loads(lancer("etat-issue.py", numero))
    print(f"Issue #{numero} : {e['titre']} (étape {e['etape']})", file=sys.stderr)
    if not e["ouverte"] or "publication" not in e["labels"]:
        print("  fermée, ou pas une demande de publication : ignorée", file=sys.stderr)
        return
    if etapes.REFUSEE in e["labels"] or not membres.est_membre(e["auteur"]):
        print(f"  @{e['auteur']} n'est pas dans la liste des membres : ignorée", file=sys.stderr)
        return
    if e["type"] is None:
        raise Echec("ni « type:evenement » ni « type:news » : impossible de choisir le gabarit")

    etape = e["etape"]
    suivi = e.get(etape, {})
    if etape == "attente":
        lancer("preparer-issue.py", numero)
        if e["publication"] is None:
            lancer("telecharger-images.py", numero, depot.propositions(numero) / "entree")
        proposer(numero, "site")
        changer_etape(numero, None, "site")
    elif etape in ("site", "linkedin") and suivi["consignes"]:
        lancer("preparer-issue.py", numero)
        proposer(numero, etape)
    elif etape == "site" and suivi["valide"]:
        lancer("preparer-issue.py", numero)
        lancer("enregistrer-vignette.py", numero)
        proposer(numero, "linkedin")
        changer_etape(numero, "site", "linkedin")
    elif etape == "linkedin" and suivi["valide"]:
        lancer("preparer-issue.py", numero)
        lancer("finaliser-pr.py", numero)
        changer_etape(numero, "linkedin", "prete")
    else:
        print(f"  rien à faire pour l'instant (étape {etape})", file=sys.stderr)
    github.retirer_label(numero, etapes.A_TRAITER)


def verifier_prerequis() -> None:
    manquants = [o for o in ("git", "gh", "claude") if not shutil.which(o)] + visuels.outils_manquants()
    if manquants:
        sys.exit("outils introuvables : " + ", ".join(manquants) + " (voir scripts/publication/README.md)")
    if etat.BOT:
        print(f"exécution par le bot {etat.BOT}", file=sys.stderr)
        return
    compte = github.gh("api", "user", "-q", ".login")
    if not membres.est_membre(compte):
        sys.exit(f"@{compte} n'est pas dans membres.txt : ses propositions ne seraient pas reconnues")


def main() -> None:
    if any(not a.isdigit() for a in sys.argv[1:]):
        sys.exit(__doc__)
    verifier_prerequis()
    depot.TRAVAIL.mkdir(exist_ok=True)
    numeros = [int(a) for a in sys.argv[1:]] or [i["number"] for i in github.gh_json(
        "issue", "list", "--state", "open", "--label", etapes.A_TRAITER, "--json", "number", "--limit", "50")]
    echecs = 0
    for numero in numeros:
        try:
            traiter(numero)
        except Echec as exc:
            echecs += 1
            print(f"  ✗ issue #{numero} : {exc}", file=sys.stderr)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
