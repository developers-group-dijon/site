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


def ecrire(*args: str, entree: str | None = None) -> None:
    """Comme gh(), pour une opération qui modifie le dépôt : simulée en mode essai."""
    if ESSAI:
        print("[essai] gh", *args, file=sys.stderr)
        if entree:
            print(textwrap.indent(entree.rstrip(), "  │ "), file=sys.stderr)
        return
    gh(*args, entree=entree)


def labels(issue: int) -> set[str]:
    donnees = json.loads(gh("issue", "view", str(issue), "--json", "labels"))
    return {label["name"] for label in donnees["labels"]}


def ajouter_label(issue: int, label: str) -> None:
    ecrire("issue", "edit", str(issue), "--add-label", label)


def commenter(issue: int, corps: str) -> None:
    ecrire("issue", "comment", str(issue), "--body-file", "-", entree=corps)


def approuver(commentaire_id: int) -> None:
    """Réaction 👍 sur un commentaire d'issue."""
    ecrire("api", "--method", "POST", f"repos/{{owner}}/{{repo}}/issues/comments/{commentaire_id}/reactions",
           "-f", "content=+1", "--silent")


def creer_label(nom: str, couleur: str, description: str) -> None:
    """Crée le label, ou met à jour sa couleur et sa description."""
    ecrire("label", "create", nom, "--color", couleur, "--description", description, "--force")
