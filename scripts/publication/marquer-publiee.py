#!/usr/bin/env python3
"""Marque comme publiée une demande dont la Pull Request a été mergée.

Usage : marquer-publiee.py ISSUE

Lancé par le gardien quand une issue de publication est fermée comme
terminée : GitHub la ferme au merge grâce au « Closes #N » de la Pull
Request et du commit « Annonce ». Si l'issue était à l'étape « prete »,
remplace « publication:prete » par « publication:publiee » et indique où
trouver le post LinkedIn. Sinon (fermeture à la main en cours de route),
ne fait rien.

Affiche « publiee » ou « ignoree ».
"""

import sys

from commun import etapes, github

PRETE = "publication:prete"
PUBLIEE = "publication:publiee"


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit(__doc__)
    issue = int(sys.argv[1])

    labels = github.labels(issue)
    if etapes.etape_en_cours(labels) != "prete":
        print("ignoree")
        return
    github.ajouter_label(issue, PUBLIEE)
    github.retirer_label(issue, PRETE)
    if etapes.A_TRAITER in labels:
        github.retirer_label(issue, etapes.A_TRAITER)
    github.commenter(issue, "La Pull Request est mergée : l'article sera en ligne dès la fin du déploiement "
                            "de production (workflow Site). Le visuel et le texte du post LinkedIn sont dans "
                            "le dossier de l'article sur `main` (`linkedin.png` et `linkedin.txt`).\n")
    print("publiee")


if __name__ == "__main__":
    main()
