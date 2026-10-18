#!/usr/bin/env python3
"""Accueille une demande de publication ouverte avec un formulaire d'issue.

Usage : accueillir-issue.py ISSUE AUTEUR

- AUTEUR est membre (membres.txt) : pose « publication:a-traiter » et répond
  avec la liste des commandes de validation.
- Sinon : pose « publication:refusee » et explique que la demande ne sera pas
  traitée automatiquement.

Affiche « a-traiter » ou « refusee ».
"""

import sys

from commun import commandes, etapes, github, membres


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    issue, auteur = int(sys.argv[1]), sys.argv[2]

    if membres.est_membre(auteur):
        github.ajouter_label(issue, etapes.A_TRAITER)
        github.commenter(issue, f"Merci @{auteur}, la demande est prise en compte. Les propositions "
                                "(trois vignettes et le texte de l'article) seront publiées ici "
                                f"en commentaire.\n\n{commandes.AIDE}")
        print("a-traiter")
    else:
        github.ajouter_label(issue, etapes.REFUSEE)
        github.commenter(issue, f"Merci @{auteur} pour cette proposition ! La publication automatique "
                                "est réservée aux membres de l'association : cette demande ne sera pas "
                                "traitée automatiquement. Un ou une membre du bureau peut la reprendre "
                                "à son compte en ouvrant une nouvelle issue.")
        print("refusee")


if __name__ == "__main__":
    main()
