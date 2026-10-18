"""Appels à GitHub par la CLI gh.

Le dépôt visé est celui du dossier courant, ou celui de la variable GH_REPO
(lue par gh lui-même), définie dans les workflows.

Avec PUBLICATION_ESSAI=1, les opérations d'écriture (labels, commentaires,
réactions) sont affichées au lieu d'être exécutées : de quoi essayer un
script sur une vraie issue sans y toucher.
"""

import json
import os
import subprocess
import sys
import textwrap

ESSAI = os.environ.get("PUBLICATION_ESSAI") == "1"


def gh(*args: str, entree: str | None = None) -> str:
    """Lance gh et renvoie sa sortie ; arrête le script en cas d'échec
    (le message d'erreur de gh reste affiché)."""
    res = subprocess.run(["gh", *args], input=entree, text=True, stdout=subprocess.PIPE)
    if res.returncode != 0:
        sys.exit(f"échec de « gh {' '.join(args[:2])} » (code {res.returncode})")
    return res.stdout.strip()


def ecrire(*args: str, entree: str | None = None) -> str:
    """Comme gh(), pour une opération qui modifie le dépôt : simulée en mode
    essai (renvoie alors "")."""
    if ESSAI:
        print("[essai] gh", *args, file=sys.stderr)
        if entree:
            print(textwrap.indent(entree.rstrip(), "  │ "), file=sys.stderr)
        return ""
    return gh(*args, entree=entree)


def gh_json(*args: str):
    return json.loads(gh(*args) or "null")


def nom_depot() -> str:
    """« propriétaire/dépôt »."""
    return gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")


def lire_issue(numero: int, champs: str) -> dict:
    """Champs d'une issue, par exemple « title,body,comments »."""
    return gh_json("issue", "view", str(numero), "--json", champs)


def labels(numero: int) -> set[str]:
    return {label["name"] for label in lire_issue(numero, "labels")["labels"]}


def ajouter_label(issue: int, label: str) -> None:
    ecrire("issue", "edit", str(issue), "--add-label", label)


def retirer_label(issue: int, label: str) -> None:
    ecrire("issue", "edit", str(issue), "--remove-label", label)


def commenter(issue: int, corps: str) -> None:
    ecrire("issue", "comment", str(issue), "--body-file", "-", entree=corps)


def approuver(commentaire_id: int) -> None:
    """Réaction 👍 sur un commentaire d'issue."""
    ecrire("api", "--method", "POST", f"repos/{{owner}}/{{repo}}/issues/comments/{commentaire_id}/reactions",
           "-f", "content=+1", "--silent")


def creer_label(nom: str, couleur: str, description: str) -> None:
    """Crée le label, ou met à jour sa couleur et sa description."""
    ecrire("label", "create", nom, "--color", couleur, "--description", description, "--force")
