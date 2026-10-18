#!/usr/bin/env python3
"""Crée ou met à jour les labels de publication du dépôt.

Usage : scripts/publication/creer-labels.py

À lancer une fois, puis après chaque modification de commun/etapes.py.
Sans danger si les labels existent déjà.
"""

import sys

from commun import github
from commun.etapes import LABELS


def main() -> None:
    if len(sys.argv) > 1:
        sys.exit(__doc__)
    for nom, (couleur, description) in LABELS.items():
        github.creer_label(nom, couleur, description)
        print(nom)


if __name__ == "__main__":
    main()
